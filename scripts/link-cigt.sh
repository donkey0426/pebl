#!/bin/bash
set -e
source libs/emsdk/emsdk_env.sh

em++ -Oz \
  -s WASM=1 \
  -s USE_SDL=2 -s USE_SDL_NET=2 -s USE_SDL_TTF=2 \
  -s USE_SDL_IMAGE=2 \
  -s 'SDL2_IMAGE_FORMATS=["png","jpg","gif","bmp"]' \
  -s USE_LIBJPEG=1 \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s INITIAL_MEMORY=67108864 \
  -s MAXIMUM_MEMORY=4294967296 \
  -s 'EXPORTED_RUNTIME_METHODS=["ccall","cwrap","FS","callMain","requestFullscreen"]' \
  -s MODULARIZE=1 \
  -s EXPORT_NAME="createPEBLModule" \
  -s FETCH=1 \
  -s FORCE_FILESYSTEM=1 \
  -s ASSERTIONS=1 \
  -s ASYNCIFY=1 \
  -s ASYNCIFY_STACK_SIZE=2097152 \
  -s 'ASYNCIFY_IMPORTS=["emscripten_sleep"]' \
  -sLZ4=1 \
  --pre-js emscripten/load-idbfs.js \
  -lidbfs.js \
  -DPEBL_EMSCRIPTEN \
  -o bin/pebl2.html \
  obj-em/src/base/lex.yy.o \
  obj-em/src/utility/re.o \
  obj-em/src/apps/PEBL.o \
  obj-em/src/base/Evaluator-es.o \
  obj-em/src/base/FunctionMap.o \
  obj-em/src/base/grammar.tab.o \
  obj-em/src/base/PEBLObject.o \
  obj-em/src/base/Loader.o \
  obj-em/src/base/PComplexData.o \
  obj-em/src/base/PList.o \
  obj-em/src/base/PNode.o \
  obj-em/src/base/VariableMap.o \
  obj-em/src/base/Variant.o \
  obj-em/src/devices/PEventLoop-es.o \
  obj-em/src/devices/PDevice.o \
  obj-em/src/devices/PEventQueue.o \
  obj-em/src/devices/PEvent.o \
  obj-em/src/devices/PKeyboard.o \
  obj-em/src/devices/PTimer.o \
  obj-em/src/devices/DeviceState.o \
  obj-em/src/devices/PStream.o \
  obj-em/src/devices/PAudioOut.o \
  obj-em/src/devices/PNetwork.o \
  obj-em/src/devices/PJoystick.o \
  obj-em/src/libs/PEBLMath.o \
  obj-em/src/libs/PEBLStream.o \
  obj-em/src/libs/PEBLObjects.o \
  obj-em/src/libs/PEBLEnvironment.o \
  obj-em/src/libs/PEBLList.o \
  obj-em/src/libs/PEBLString.o \
  obj-em/src/libs/PEBLLSL.o \
  obj-em/src/objects/PEnvironment.o \
  obj-em/src/objects/PWidget.o \
  obj-em/src/objects/PWindow.o \
  obj-em/src/objects/PImageBox.o \
  obj-em/src/objects/PCanvas.o \
  obj-em/src/objects/PColor.o \
  obj-em/src/objects/PDrawObject.o \
  obj-em/src/objects/PFont.o \
  obj-em/src/objects/PTextObject.o \
  obj-em/src/objects/PLabel.o \
  obj-em/src/objects/PTextBox.o \
  obj-em/src/objects/PMovie.o \
  obj-em/src/objects/PCustomObject.o \
  obj-em/src/utility/PEBLUtility.o \
  obj-em/src/utility/PError.o \
  obj-em/src/utility/BinReloc.o \
  obj-em/src/utility/PEBLPath.o \
  obj-em/src/utility/PEBLHTTP.o \
  obj-em/src/utility/md5.o \
  obj-em/src/utility/FontCache.o \
  obj-em/src/utility/FormatParser.o \
  obj-em/src/utility/PLabStreamingLayer.o \
  obj-em/src/platforms/sdl/PlatformEnvironment.o \
  obj-em/src/platforms/sdl/PlatformWidget.o \
  obj-em/src/platforms/sdl/PlatformWindow.o \
  obj-em/src/platforms/sdl/PlatformImageBox.o \
  obj-em/src/platforms/sdl/PlatformKeyboard.o \
  obj-em/src/platforms/sdl/PlatformFont.o \
  obj-em/src/platforms/sdl/PlatformLabel.o \
  obj-em/src/platforms/sdl/PlatformTextBox.o \
  obj-em/src/platforms/sdl/PlatformTimer.o \
  obj-em/src/platforms/sdl/PlatformDrawObject.o \
  obj-em/src/platforms/sdl/PlatformCanvas.o \
  obj-em/src/platforms/sdl/SDLUtility.o \
  obj-em/src/platforms/sdl/PlatformEventQueue.o \
  obj-em/src/platforms/sdl/PlatformAudioOut.o \
  obj-em/src/platforms/sdl/PlatformNetwork.o \
  obj-em/src/platforms/sdl/PlatformJoystick.o \
  obj-em/src/platforms/sdl/PlatformAudioIn.o \
  libs/SDL2_gfx-1.0.4/build-em/SDL2_gfxPrimitives.o \
  --shell-file emscripten/shell_PEBL_debug.html \
  --preload-file emscripten/pebl-lib@/usr/local/share/pebl2/pebl-lib \
  --preload-file emscripten/media/@/usr/local/share/pebl2/media \
  --preload-file battery/cigt@/usr/local/share/pebl2/battery/cigt
