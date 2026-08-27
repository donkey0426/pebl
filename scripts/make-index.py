import os

html = """\
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>cIGT Task</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
   html, body { width: 100%; height: 100%; background: #000; overflow: auto; margin: 0; -webkit-overflow-scrolling: touch; }
    #canvas-container { min-width: 100vw; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
    canvas { display: block; background: #fff; }
    #status { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%); color: white; font-family: sans-serif; font-size: 18px; text-align: center; }
    #rotate-prompt { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 20000; color: white; font-family: sans-serif; align-items: center; justify-content: center; text-align: center; padding: 20px; }
    #rotate-prompt.show { display: flex; }
    #rotate-icon { font-size: 56px; margin-bottom: 20px; animation: rotateHint 1.5s ease-in-out infinite; }
    @keyframes rotateHint { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(90deg); } }
    #q-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }
    #q-overlay.show { display: flex; }
    #q-box { text-align: center; padding: 40px; max-width: 600px; }
    #q-box p { color: white; font-size: 20px; margin-bottom: 12px; line-height: 1.6; }
    #q-box .sub { color: #ccc; font-size: 15px; margin-bottom: 32px; }
    #q-btn { display: inline-block; padding: 16px 48px; background: #1a73e8; color: white; text-decoration: none; border-radius: 8px; font-size: 20px; font-weight: bold; opacity: 0; pointer-events: none; transition: opacity .3s; }
    #q-btn.ready { opacity: 1; pointer-events: auto; }
    #q-btn:hover { background: #1557b0; }
    #upload-status { color: #ffd54f; font-size: 15px; margin-bottom: 20px; min-height: 20px; }
    #upload-status.ok { color: #81c784; }
    #upload-status.fail { color: #e57373; }
  </style>
</head>
<body>
  <div id="status">Loading...</div>
  <div id="rotate-prompt">
    <div>
      <div id="rotate-icon">&#128241;</div>
      <div style="font-size:20px; margin-bottom:10px;">請將手機轉為橫向繼續作業</div>
      <div style="font-size:15px; color:#ccc;">Please rotate your device to landscape to continue</div>
    </div>
  </div>
  <div id="canvas-container">
    <canvas id="canvas" oncontextmenu="event.preventDefault()"></canvas>
  </div>
  <div id="q-overlay">
    <div id="q-box">
      <p>\u611f\u8b1d\u60a8\u7684\u53c3\u8207\uff0c\u63a5\u4e0b\u4f86\u9ebb\u7169\u60a8\u6309\u4e0b\u65b9\u7684\u6309\u9215\uff0c\u9032\u5165\u4e0b\u500b\u968e\u6bb5\u3002</p>
      <p class="sub">Thank you for participating. Please click the button below to proceed to the next stage.</p>
      <div id="upload-status">資料上傳中，請稍候，勿關閉此頁面... / Uploading your data, please wait, do not close this page...</div>
      <a id="q-btn" href="#">進入問卷 / Start Questionnaire</a>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/eruda"></script>
  <script>eruda.init();</script>
  <script src="pebl2.js"></script>
  <script>
    var canvas = document.getElementById('canvas');
    function resizeCanvas() {
      var gameW = 1280, gameH = 720;
      var scale = Math.min(window.innerWidth / gameW, window.innerHeight / gameH);
      var w = (gameW * scale) + 'px';
      var h = (gameH * scale) + 'px';
      if (canvas.style.width !== w) canvas.style.setProperty('width', w, 'important');
      if (canvas.style.height !== h) canvas.style.setProperty('height', h, 'important');
      requestAnimationFrame(resizeCanvas);
    }
    resizeCanvas();

    var rotatePrompt = document.getElementById('rotate-prompt');
    function checkOrientation() {
      var isPortraitPhone = window.innerWidth < window.innerHeight && window.innerWidth < 900;
      rotatePrompt.classList.toggle('show', isPortraitPhone);
    }
    window.addEventListener('resize', checkOrientation);
    window.addEventListener('orientationchange', checkOrientation);
    checkOrientation();


    var participant = new URLSearchParams(window.location.search).get('participant') || 'P' + Math.floor(Math.random() * 900000 + 100000);
    var lang = new URLSearchParams(window.location.search).get('lang') || 'zh';
    var taskFinished = false;
    var taskStarted = false;
    var peblInstance = null;
    var dataUploaded = false;
    var uploadInProgress = false;

    var GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/AKfycbwmzLzlVqizQH6yGk4FQ2YHSXPRIinEV_IvIanY7MsPjZS1ywl1GdZec6TAwt89OOlqqg/exec';

    // 上傳中/離開頁面警告：避免受試者在資料還沒存完就關閉分頁
    window.addEventListener('beforeunload', function(e) {
      if (uploadInProgress) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    });

    function setUploadStatusUI(state) {
      var el = document.getElementById('upload-status');
      var btn = document.getElementById('q-btn');
      if (state === 'uploading') {
        el.textContent = '資料上傳中，請稍候，勿關閉此頁面... / Uploading your data, please wait, do not close this page...';
        el.className = '';
        btn.classList.remove('ready');
      } else if (state === 'retrying') {
        el.textContent = '上傳重試中... / Retrying upload...';
        el.className = '';
        btn.classList.remove('ready');
      } else if (state === 'success') {
        el.textContent = '資料已成功上傳 ✓ / Data uploaded successfully ✓';
        el.className = 'ok';
        btn.classList.add('ready');
      } else if (state === 'failed') {
        el.textContent = '上傳失敗，但資料已於本機備份，請聯絡研究人員 / Upload failed, but a local backup was saved. Please contact the researcher.';
        el.className = 'fail';
        btn.classList.add('ready');
      }
    }

    function backupToLocalStorage(csvContent) {
      try {
        localStorage.setItem('cigt_backup_' + participant, csvContent);
        console.warn('[PEBL] CSV backed up to localStorage as fallback');
      } catch (e) {
        console.error('[PEBL] localStorage backup also failed:', e);
      }
    }

    function uploadCSVToGoogleSheets(retriesLeft) {
      if (dataUploaded) return;
      if (typeof retriesLeft === 'undefined') retriesLeft = 3;
      uploadInProgress = true;
      setUploadStatusUI(retriesLeft === 3 ? 'uploading' : 'retrying');

      var csvContent;
      try {
        var csvPath = '/usr/local/share/pebl2/battery/cigt/data/' + participant + '/cigtlog-' + participant + '.csv';
        csvContent = peblInstance.FS.readFile(csvPath, { encoding: 'utf8' });
      } catch (e) {
        console.error('[PEBL] Could not read CSV file:', e);
        uploadInProgress = false;
        setUploadStatusUI('failed');
        return;
      }

      console.log('[PEBL] CSV read OK, uploading to Google Sheets... (attempt', 4 - retriesLeft, ')');
      fetch(GOOGLE_SHEETS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({ participant: participant, csv: csvContent })
      }).then(function() {
        dataUploaded = true;
        uploadInProgress = false;
        console.log('[PEBL] Uploaded to Google Sheets successfully');
        setUploadStatusUI('success');
      }).catch(function(err) {
        console.error('[PEBL] Google Sheets upload failed:', err);
        if (retriesLeft > 0) {
          setTimeout(function() { uploadCSVToGoogleSheets(retriesLeft - 1); }, 2000);
        } else {
          uploadInProgress = false;
          backupToLocalStorage(csvContent);
          setUploadStatusUI('failed');
        }
      });
    }

    function showQuestionnaire() {
      if (taskFinished) return;
      taskFinished = true;
      document.getElementById('canvas-container').style.display = 'none';
      document.getElementById('q-btn').href = 'questionnaire.html?participant=' + participant;
      document.getElementById('q-overlay').classList.add('show');
      // 不論是從哪個結束偵測路徑觸發，這裡都會確保資料被上傳(含重試機制)
      uploadCSVToGoogleSheets();
    }

    document.addEventListener('peblTestComplete', function(e) {
      console.log('[PEBL] peblTestComplete event received', e.detail);
      showQuestionnaire();
    });

    var Module = {
      noInitialRun: true,
      canvas: canvas,
      print: function(t) {
        console.log('[PEBL]', t);
        if (taskStarted && t && (
          t.indexOf('PEBL test completed') >= 0 ||
          t.indexOf('exitCode') >= 0 ||
          t.indexOf('Exiting PEBL') >= 0
        )) {
          setTimeout(showQuestionnaire, 1500);
        }
      },
      printErr: function(t) {
        console.error('[PEBL ERR]', t);
        if (taskStarted && t && (
          t.indexOf('PEBL test completed') >= 0 ||
          t.indexOf('exitCode') >= 0 ||
          t.indexOf('Exiting PEBL') >= 0
        )) {
          setTimeout(showQuestionnaire, 1500);
        }
      },
      setStatus: function(t) {
        var s = document.getElementById('status');
        if (s) { s.innerHTML = t || ''; if (!t) s.style.display = 'none'; }
      },
      onExit: function(code) {
        console.log('[PEBL] onExit called, code=', code);
        if (taskStarted) { setTimeout(showQuestionnaire, 1000); }
      }
    };

    createPEBLModule(Module).then(function(instance) {
      peblInstance = instance;
      document.getElementById('status').style.display = 'none';
      taskStarted = true;
      instance.callMain(['/usr/local/share/pebl2/battery/cigt/cigt.pbl', '-s', participant, '--language', lang, '--display', '1280x720']);
    });
  </script>
</body>
</html>
"""

os.makedirs('site', exist_ok=True)
with open('site/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html written successfully")
