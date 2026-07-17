import os

html = """\
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>cIGT Task</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; background: #000; overflow: hidden; display: flex; align-items: center; justify-content: center; }
    #canvas-container { width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; }
    canvas { display: block; background: #fff; }
    #status { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%); color: white; font-family: sans-serif; font-size: 18px; text-align: center; }
    #q-overlayr { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }
    #q-overlay.show { display: flex; }
    #q-box { text-align: center; padding: 40px; max-width: 600px; }
    #q-box p { color: white; font-size: 20px; margin-bottom: 12px; line-height: 1.6; }
    #q-box .sub { color: #ccc; font-size: 15px; margin-bottom: 32px; }
    #q-btn { display: inline-block; padding: 16px 48px; background: #1a73e8; color: white; text-decoration: none; border-radius: 8px; font-size: 20px; font-weight: bold; }
    #q-btn:hover { background: #1557b0; }
  </style>
</head>
<body>
  <div id="status">Loading...</div>
  <div id="canvas-container">
    <canvas id="canvas" oncontextmenu="event.preventDefault()"></canvas>
  </div>
  <div id="q-overlay">
    <div id="q-box">
      <p>\u611f\u8b1d\u60a8\u7684\u53c3\u8207\uff0c\u63a5\u4e0b\u4f86\u9ebb\u7169\u60a8\u6309\u4e0b\u65b9\u7684\u6309\u9215\uff0c\u9032\u5165\u4e0b\u500b\u968e\u6bb5\u3002</p>
      <p class="sub">Thank you for participating. Please click the button below to proceed to the next stage.</p>
      <a id="q-btn" href="#">\u9032\u5165\u554f\u5377 / Start Questionnaire</a>
    </div>
  </div>
  <script src="pebl2.js"></script>
  <script>
    var canvas = document.getElementById('canvas');

function resizeCanvas() {
      var gameW = 1280, gameH = 720;
      var scale = Math.min(window.innerWidth / gameW, window.innerHeight / gameH);
      canvas.style.setProperty('width', (gameW * scale) + 'px', 'important');
      canvas.style.setProperty('height', (gameH * scale) + 'px', 'important');
    }
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('orientationchange', resizeCanvas);
    resizeCanvas();
    setInterval(resizeCanvas, 500);

    var participant = new URLSearchParams(window.location.search).get('participant') || 'P' + Math.floor(Math.random() * 900000 + 100000);
    var lang = new URLSearchParams(window.location.search).get('lang') || 'zh';
    var taskFinished = false;
    var taskStarted = false;
    var peblInstance = null;

    var GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/AKfycbwmzLzlVqizQH6yGk4FQ2YHSXPRIinEV_IvIanY7MsPjZS1ywl1GdZec6TAwt89OOlqqg/exec';
   function showQuestionnaire() {
      if (taskFinished) return;
      taskFinished = true;
      document.getElementById('q-btn').href = 'questionnaire.html?participant=' + participant;
      document.getElementById('q-overlay').classList.add('show');
    }

    function uploadCSVToGoogleSheets() {
      try {
        var csvPath = '/usr/local/share/pebl2/battery/cigt/data/' + participant + '/cigtlog-' + participant + '.csv';
        var csvContent = peblInstance.FS.readFile(csvPath, { encoding: 'utf8' });
        console.log('[PEBL] CSV read OK, uploading to Google Sheets...');
        fetch(GOOGLE_SHEETS_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify({ participant: participant, csv: csvContent })
        }).then(function() {
          console.log('[PEBL] Uploaded to Google Sheets successfully');
        }).catch(function(err) {
          console.error('[PEBL] Google Sheets upload failed:', err);
        });
      } catch (e) {
        console.error('[PEBL] Could not read CSV file:', e);
      }
    }

    document.addEventListener('peblTestComplete', function(e) {
      console.log('[PEBL] peblTestComplete event received', e.detail);
      uploadCSVToGoogleSheets();
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
      instance.callMain(['/usr/local/share/pebl2/battery/cigt/cigt.pbl', '-s', participant, '--language', lang]);
    });
  </script>
</body>
</html>
"""

os.makedirs('site', exist_ok=True)
with open('site/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html written successfully")
