<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>歌伴侣 - 智能伴奏大师</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        gold: {
                            50: '#fbf7ee',
                            100: '#f5ebd2',
                            200: '#ebd4a3',
                            300: '#deb86e',
                            400: '#cf9841',
                            500: '#b87926',
                            600: '#9b5d1e',
                            700: '#7c441a',
                            800: '#64361a',
                            900: '#522d18',
                            950: '#2f160a',
                        },
                        dark: {
                            800: '#1a1a1a',
                            850: '#141414',
                            900: '#0f0f11',
                            950: '#08080a',
                        }
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <!-- Google Fonts for retro/digital look -->
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <!-- Inline Custom Styles -->
    <style>
        body {
            background-color: #08080a;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        /* Brushed metal texture emulation */
        .brushed-panel {
            background: linear-gradient(145deg, #151518 0%, #0c0c0e 100%);
            box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05), 0 10px 25px -5px rgba(0,0,0,0.5);
            border: 1px solid rgba(222, 184, 110, 0.15);
        }
        .gold-glow {
            box-shadow: 0 0 15px rgba(222, 184, 110, 0.35);
        }
        .gold-glow-strong {
            box-shadow: 0 0 25px rgba(222, 184, 110, 0.6);
        }
        .neon-border {
            border: 1px solid rgba(222, 184, 110, 0.4);
        }
        /* Custom scrollbar for beautiful lists */
        ::-webkit-scrollbar {
            width: 4px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(222, 184, 110, 0.3);
            border-radius: 2px;
        }
        /* Gold metallic text gradient */
        .text-gold-gradient {
            background: linear-gradient(135deg, #ffe3a8 0%, #cf9841 50%, #9b5d1e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        /* VU Meter animation */
        @keyframes vu-bounce {
            0%, 100% { height: 10%; }
            50% { height: var(--target-height, 80%); }
        }
        .vu-bar {
            animation: vu-bounce 0.5s ease-in-out infinite;
        }
    </style>
</head>
<body class="text-gray-200 min-h-screen flex flex-col justify-between overflow-x-hidden font-sans">

    <!-- Top Status / Brand Header -->
    <header class="w-full max-w-md mx-auto pt-5 px-5 flex justify-between items-center z-10">
        <div class="flex items-center space-x-2.5">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-yellow-600 flex items-center justify-center shadow-lg border border-yellow-200">
                <!-- Golden Retro Microphone SVG -->
                <svg class="w-5.5 h-5.5 text-stone-950" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3zm5 9a1 1 0 0 1-1 1 5 5 0 0 1-8 0 1 1 0 0 1-1-1 1 1 0 0 0-2 0 7 7 0 0 0 6 6.93V21h-3a1 1 0 0 0 0 2h8a1 1 0 0 0 0-2h-3v-3.07A7 7 0 0 0 20 11a1 1 0 0 0-2 0z"/>
                </svg>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-wide text-gold-gradient">歌伴侣</h1>
                <p class="text-[10px] tracking-widest text-amber-500/80 font-bold uppercase">Professional Vocal Partner</p>
            </div>
        </div>
        <!-- Premium Badge -->
        <div class="px-3 py-1.5 rounded-full border border-amber-500/40 bg-amber-500/10 text-amber-300 text-xs font-semibold tracking-wider flex items-center space-x-1">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span>发烧级金牌控制台</span>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-grow w-full max-w-md mx-auto px-4 py-4 flex flex-col justify-start relative">

        <!-- Toast Box -->
        <div id="toast" class="fixed top-24 left-1/2 transform -translate-x-1/2 z-50 bg-stone-900 border border-amber-400/80 text-amber-100 px-5 py-3 rounded-xl shadow-2xl flex items-center space-x-3 text-sm opacity-0 pointer-events-none transition-all duration-300 max-w-xs text-center">
            <svg class="w-5 h-5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span id="toast-text" class="font-medium">消息提示</span>
        </div>

        <!-- PAGE 1: INPUT GATEWAY -->
        <section id="page-1" class="w-full flex flex-col space-y-5 transition-all duration-500 ease-in-out">
            
            <!-- Intro Card -->
            <div class="p-5 rounded-2xl brushed-panel relative overflow-hidden">
                <div class="absolute -right-12 -top-12 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl"></div>
                <h2 class="text-lg font-bold text-amber-300 flex items-center space-x-2">
                    <span class="text-xl">✨</span>
                    <span>欢迎使用，老歌友！</span>
                </h2>
                <p class="text-sm text-gray-400 mt-2 leading-relaxed">
                    在这里，您可以轻松把<span class="text-amber-400 font-semibold">抖音视频</span>或<span class="text-amber-400 font-semibold">手机里的录音</span>变成完美的<span class="text-emerald-400 font-semibold">伴奏</span>，还可以自由升调、降调，让唱歌更轻松、更好听！
                </p>
            </div>

            <!-- ENTRANCE A: Douyin Extraction -->
            <div class="p-5 rounded-2xl brushed-panel relative">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold tracking-widest text-amber-500/60 uppercase">方法一 / 抖音伴奏一键提取</span>
                    <span class="text-[11px] bg-red-600/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded font-semibold">推荐</span>
                </div>
                
                <h3 class="text-lg font-semibold text-white flex items-center space-x-2">
                    <span class="p-1 rounded-lg bg-gradient-to-br from-stone-800 to-stone-900 border border-amber-500/30">
                        <!-- Douyin Note Icon -->
                        <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2v14a4 4 0 1 1-4-4 4 4 0 0 1 4 4zm0 0a8.5 8.5 0 0 0 8.5-8.5H16A4.5 4.5 0 0 1 12 12z"/>
                        </svg>
                    </span>
                    <span>从抖音提取伴奏</span>
                </h3>

                <!-- Help Link for elders -->
                <button onclick="toggleHelpPopup(true)" class="mt-2 text-xs text-amber-400/90 underline flex items-center space-x-1 active:text-amber-300">
                    <span>💡 不知道怎么复制抖音链接？点我查看超大字图文教程</span>
                </button>

                <!-- Clipboard Input Area -->
                <div class="mt-4 space-y-3">
                    <textarea id="douyin-input" rows="3" 
                        class="w-full bg-black/60 border-2 border-stone-800 focus:border-amber-500/80 rounded-xl p-3.5 text-base text-gray-200 placeholder-gray-500 transition-colors focus:outline-none resize-none font-medium"
                        placeholder="在此处长按【粘贴】抖音复制来的文字或链接...&#10;例如：7.80 对话框里的精彩 https://v.douyin.com/abc/"></textarea>
                    
                    <div class="flex space-x-2">
                        <button onclick="pasteFromClipboard()" class="flex-1 py-3 bg-stone-800/80 hover:bg-stone-800 border border-amber-500/30 text-amber-300 rounded-xl font-bold text-sm tracking-wide transition active:scale-95 flex items-center justify-center space-x-1.5 shadow-md">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                            <span>自动识别粘贴</span>
                        </button>
                        <button onclick="processDouyin()" class="flex-[1.5] py-3.5 bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-500 text-stone-950 font-black rounded-xl text-base tracking-wide transition active:scale-95 gold-glow-strong flex items-center justify-center space-x-2">
                            <span>✨ 开始智能提取</span>
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- ENTRANCE B: Audio Upload -->
            <div class="p-5 rounded-2xl brushed-panel relative">
                <span class="text-xs font-bold tracking-widest text-amber-500/60 uppercase">方法二 / 手机本地已有录音</span>
                
                <h3 class="text-lg font-semibold text-white mt-2 flex items-center space-x-2">
                    <span class="p-1 rounded-lg bg-gradient-to-br from-stone-800 to-stone-900 border border-amber-500/30">
                        <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                        </svg>
                    </span>
                    <span>上传已有的录音或音频</span>
                </h3>

                <!-- Drag-and-drop zone style -->
                <div class="mt-4 border-2 border-dashed border-stone-800 hover:border-amber-500/40 rounded-xl bg-black/40 p-6 text-center cursor-pointer relative group transition-all" onclick="triggerFileInput()">
                    <input type="file" id="audio-file" accept=".mp3,.wav,.m4a" class="hidden" onchange="handleFileSelected(event)">
                    <div class="flex flex-col items-center space-y-3">
                        <div class="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center border border-amber-500/20 group-hover:bg-amber-500/20 transition">
                            <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </div>
                        <div>
                            <p class="text-base font-bold text-gray-200">点击选择手机里的音频文件</p>
                            <p class="text-xs text-gray-500 mt-1.5 leading-relaxed">支持格式：MP3, M4A, WAV<br>大小不超过 20MB（适合常规歌曲伴奏）</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Show-off / Trust Banner -->
            <div class="flex justify-around items-center py-2 px-1 text-center text-[11px] text-gray-500">
                <div class="flex flex-col items-center">
                    <span class="text-base text-amber-500">🛡️</span>
                    <span class="mt-0.5">隐私安全保密</span>
                </div>
                <div class="border-r border-stone-800 h-6"></div>
                <div class="flex flex-col items-center">
                    <span class="text-base text-amber-500">⚡</span>
                    <span class="mt-0.5">极速无损转换</span>
                </div>
                <div class="border-r border-stone-800 h-6"></div>
                <div class="flex flex-col items-center">
                    <span class="text-base text-amber-500">🎧</span>
                    <span class="mt-0.5">高品质发烧音质</span>
                </div>
            </div>

        </section>

        <!-- PROCESSING SCREEN (HIDDEN BY DEFAULT) -->
        <section id="processing-screen" class="hidden w-full flex flex-col items-center justify-center py-16 px-4 text-center space-y-6">
            <div class="relative w-32 h-32 flex items-center justify-center">
                <!-- Rotating luxury border -->
                <div class="absolute inset-0 rounded-full border-4 border-dashed border-amber-500/40 animate-spin" style="animation-duration: 8s;"></div>
                <!-- Pulsing center core -->
                <div class="w-24 h-24 rounded-full bg-gradient-to-br from-stone-900 to-black border-2 border-amber-400 flex flex-col items-center justify-center gold-glow">
                    <span class="text-xs font-bold text-amber-400" id="progress-percent">0%</span>
                    <span class="text-[9px] text-gray-500 uppercase tracking-widest mt-0.5">Processing</span>
                </div>
            </div>
            
            <div class="space-y-2">
                <h3 class="text-xl font-bold text-white tracking-wide" id="processing-step">正在连接云端发烧级音频处理器...</h3>
                <p class="text-sm text-gray-500 px-6">我们正在使用高级AI算法提取无损伴奏，请老人家稍微等几秒钟，好音乐马上呈现！</p>
            </div>

            <!-- Mock progress steps visual indicator -->
            <div class="w-full max-w-xs bg-stone-900/60 border border-stone-800 rounded-xl p-3 text-left space-y-2">
                <div class="flex items-center space-x-2 text-xs text-amber-400/80" id="step-1-indicator">
                    <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                    <span>正在获取音频通道数据...</span>
                </div>
                <div class="flex items-center space-x-2 text-xs text-gray-600" id="step-2-indicator">
                    <span class="w-2 h-2 rounded-full bg-gray-600"></span>
                    <span>正在过滤原唱人声，提取纯伴奏...</span>
                </div>
                <div class="flex items-center space-x-2 text-xs text-gray-600" id="step-3-indicator">
                    <span class="w-2 h-2 rounded-full bg-gray-600"></span>
                    <span>高品质发烧级重组输出中...</span>
                </div>
            </div>
        </section>

        <!-- PAGE 2: RESULT & AUDIO CONTROL CONSOLE -->
        <section id="page-2" class="hidden w-full flex flex-col space-y-5 transition-all duration-500 ease-in-out">
            
            <!-- SECTION 1: Audio Playback Dashboard -->
            <div class="p-5 rounded-2xl brushed-panel relative flex flex-col items-center">
                <!-- Back to start -->
                <button onclick="backToHome()" class="absolute left-4 top-4 px-3 py-1.5 rounded-lg bg-stone-800 border border-stone-700/80 text-xs text-gray-300 font-bold flex items-center space-x-1 active:bg-stone-700">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"></path></svg>
                    <span>换一首歌</span>
                </button>

                <!-- Status indicator light -->
                <div class="absolute right-4 top-4 flex items-center space-x-1.5 bg-black/40 border border-emerald-500/30 px-2 py-1 rounded-full">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Hi-Res Pure</span>
                </div>

                <!-- Vinyl/CD Visualizer simulation -->
                <div class="w-32 h-32 rounded-full bg-gradient-to-r from-stone-950 via-stone-900 to-stone-950 border-4 border-stone-800 shadow-2xl flex items-center justify-center relative mt-6 group">
                    <!-- Retro Vinyl grooves -->
                    <div class="absolute inset-2 rounded-full border border-stone-800/40"></div>
                    <div class="absolute inset-5 rounded-full border border-stone-800/60"></div>
                    <div class="absolute inset-8 rounded-full border border-stone-800/80"></div>
                    <!-- Golden core label -->
                    <div id="vinyl-disc" class="w-12 h-12 rounded-full bg-gradient-to-tr from-amber-500 to-yellow-300 flex items-center justify-center shadow-inner">
                        <div class="w-3 h-3 rounded-full bg-stone-950"></div>
                    </div>
                </div>

                <!-- Current playing accompaniment details -->
                <div class="text-center mt-4 w-full">
                    <h4 class="text-xl font-bold text-white tracking-wide truncate px-2" id="current-song-title">提取成功的抖音歌曲伴奏</h4>
                    
                    <!-- Dynamic Tone/Key Version Tag -->
                    <div class="mt-2 inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/40 text-sm font-black text-amber-300">
                        <span id="tuning-badge-icon">🎵</span>
                        <span id="current-key-display">当前版本：原调 (未作修改)</span>
                    </div>
                </div>

                <!-- Live Audio Visualizer Graphics (Seniors love watching this bounce!) -->
                <div class="w-full h-10 mt-6 flex justify-between items-end px-4 overflow-hidden relative">
                    <div class="absolute inset-x-0 bottom-0 h-0.5 bg-stone-800"></div>
                    <!-- VU Bars -->
                    <div class="vu-bar w-[3.5%] bg-amber-600 rounded-t" style="--target-height: 85%; animation-delay: 0.1s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-500 rounded-t" style="--target-height: 40%; animation-delay: 0.3s;"></div>
                    <div class="vu-bar w-[3.5%] bg-yellow-400 rounded-t" style="--target-height: 75%; animation-delay: 0.5s;"></div>
                    <div class="vu-bar w-[3.5%] bg-yellow-300 rounded-t" style="--target-height: 60%; animation-delay: 0.2s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-400 rounded-t" style="--target-height: 90%; animation-delay: 0.4s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-500 rounded-t" style="--target-height: 50%; animation-delay: 0.6s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-600 rounded-t" style="--target-height: 80%; animation-delay: 0.15s;"></div>
                    <div class="vu-bar w-[3.5%] bg-yellow-400 rounded-t" style="--target-height: 65%; animation-delay: 0.35s;"></div>
                    <div class="vu-bar w-[3.5%] bg-yellow-300 rounded-t" style="--target-height: 95%; animation-delay: 0.55s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-400 rounded-t" style="--target-height: 45%; animation-delay: 0.25s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-500 rounded-t" style="--target-height: 70%; animation-delay: 0.45s;"></div>
                    <div class="vu-bar w-[3.5%] bg-amber-600 rounded-t" style="--target-height: 90%; animation-delay: 0.65s;"></div>
                </div>

                <!-- Custom Audio Control Slider (BIG TARGET) -->
                <div class="w-full mt-4 px-2">
                    <div class="flex justify-between text-[11px] text-gray-500 font-mono mb-1">
                        <span id="player-time-current">0:00</span>
                        <span id="player-time-total">0:15</span>
                    </div>
                    <!-- Slider Container -->
                    <div class="h-4 w-full flex items-center cursor-pointer" onclick="seekAudio(event)" id="slider-track">
                        <div class="h-2 w-full bg-stone-900 rounded-full overflow-hidden relative border border-stone-800">
                            <!-- Played progress -->
                            <div id="player-progress-bar" class="h-full bg-gradient-to-r from-amber-600 to-yellow-400 w-0"></div>
                        </div>
                    </div>
                </div>

                <!-- Playback Core Buttons -->
                <div class="flex items-center justify-center space-x-6 mt-4 w-full">
                    <!-- Skip back 5s -->
                    <button onclick="skipTime(-5)" class="w-12 h-12 rounded-full bg-stone-900 border border-stone-800 flex items-center justify-center text-gray-300 active:scale-95 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.334 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z"></path>
                        </svg>
                    </button>

                    <!-- Large glowing Golden Play/Pause Trigger -->
                    <button onclick="toggleAudio()" class="w-20 h-20 rounded-full bg-gradient-to-br from-amber-500 to-yellow-300 text-stone-950 flex items-center justify-center shadow-xl active:scale-95 transition gold-glow-strong border-2 border-yellow-200">
                        <div id="play-button-icon">
                            <!-- Play Icon -->
                            <svg class="w-9 h-9 fill-current" viewBox="0 0 24 24">
                                <path d="M8 5v14l11-7z"/>
                            </svg>
                        </div>
                    </button>

                    <!-- Skip forward 5s -->
                    <button onclick="skipTime(5)" class="w-12 h-12 rounded-full bg-stone-900 border border-stone-800 flex items-center justify-center text-gray-300 active:scale-95 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.934 12.8a1 1 0 000-1.6l-5.334-4A1 1 0 005 8v8a1 1 0 001.6.8l5.334-4zM19.934 12.8a1 1 0 000-1.6l-5.334-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.334-4z"></path>
                        </svg>
                    </button>
                </div>

                <!-- Primary Action Buttons (Download & Copy Link) -->
                <div class="grid grid-cols-2 gap-3 w-full mt-6">
                    <!-- Download accompaniment -->
                    <button onclick="simulateDownload()" class="py-3.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-stone-950 font-black rounded-xl text-base tracking-wide flex items-center justify-center space-x-1.5 active:scale-95 shadow-md">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                        </svg>
                        <span>保存伴奏到手机</span>
                    </button>
                    <!-- Share & Copy Link -->
                    <button onclick="copyAccompanimentLink()" class="py-3.5 bg-stone-900 border-2 border-amber-500/40 text-amber-300 font-bold rounded-xl text-base tracking-wide flex items-center justify-center space-x-1.5 active:scale-95 shadow-md">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M8.684 10.742l4.755-3.17M12.427 12.188l4.754 3.17M15.57 12a3.001 3.001 0 11-6 0 3.001 3.001 0 016 0zM12 5.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm0 15.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"></path>
                        </svg>
                        <span>发给微信好友</span>
                    </button>
                </div>

                <!-- Expire Reminder info -->
                <div class="mt-4 text-[11px] text-gray-500 flex items-center space-x-1">
                    <span>🕒</span>
                    <span>下载链接有效期至：<span id="expire-date" class="font-mono text-amber-500/80 font-bold">2026.05.24</span>（过期请重新生成）</span>
                </div>
            </div>

            <!-- SECTION 2: Pitch Modulation Device Panel -->
            <div class="p-5 rounded-2xl brushed-panel relative flex flex-col">
                <span class="text-xs font-bold tracking-widest text-amber-500/60 uppercase">专业伴奏变调台</span>
                
                <h3 class="text-lg font-semibold text-white mt-1.5 flex items-center space-x-2">
                    <span class="p-1 rounded-lg bg-gradient-to-br from-stone-800 to-stone-900 border border-amber-500/30">
                        <!-- Sound wave/mixer icon -->
                        <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
                        </svg>
                    </span>
                    <span>唱不动？太低沉？帮您改调！</span>
                </h3>

                <!-- Controls segment: Direction (Raise/Lower) -->
                <div class="mt-4 grid grid-cols-2 gap-3">
                    <button id="btn-raise-key" onclick="selectPitchDirection('raise')" class="py-3 rounded-xl border-2 border-amber-500 bg-amber-500/10 text-amber-300 font-black text-lg flex items-center justify-center space-x-2 transition">
                        <span class="text-xl">📈</span>
                        <span>调高一点 (升调)</span>
                    </button>
                    <button id="btn-lower-key" onclick="selectPitchDirection('lower')" class="py-3 rounded-xl border border-stone-800 bg-stone-900/60 text-gray-400 font-bold text-lg flex items-center justify-center space-x-2 transition">
                        <span class="text-xl">📉</span>
                        <span>调低一点 (降调)</span>
                    </button>
                </div>

                <!-- Semi-Tone Selector (BIG ROUNDED GRID BUTTONS) -->
                <div class="mt-4">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm font-bold text-gray-300">选择要升/降几个音阶（半音）：</span>
                        <span class="text-xs text-amber-400/90 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20" id="current-steps-text">已调 1 个半音</span>
                    </div>

                    <!-- Steps Slider Grid (Elders love seeing definite buttons to click!) -->
                    <div class="grid grid-cols-6 gap-2">
                        <!-- Key steps buttons 1 to 11 -->
                        <button onclick="setSemitone(1)" class="semitone-btn py-3 rounded-xl text-stone-950 bg-amber-500 border border-amber-300 font-black text-lg transition active:scale-95 shadow-md">1</button>
                        <button onclick="setSemitone(2)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">2</button>
                        <button onclick="setSemitone(3)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">3</button>
                        <button onclick="setSemitone(4)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">4</button>
                        <button onclick="setSemitone(5)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">5</button>
                        <button onclick="setSemitone(6)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">6</button>
                        <button onclick="setSemitone(7)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">7</button>
                        <button onclick="setSemitone(8)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">8</button>
                        <button onclick="setSemitone(9)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">9</button>
                        <button onclick="setSemitone(10)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">10</button>
                        <button onclick="setSemitone(11)" class="semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95">11</button>
                        <!-- Back to original key button -->
                        <button onclick="resetToOriginal()" class="py-3 rounded-xl text-stone-950 bg-yellow-400 border border-yellow-200 font-black text-xs tracking-tight transition active:scale-95 shadow">原调</button>
                    </div>

                    <!-- Easy-to-understand musical theory explanation -->
                    <div class="mt-3 bg-black/40 p-3 rounded-xl border border-stone-800/80 text-xs text-gray-400 space-y-1">
                        <p class="flex items-center space-x-1">
                            <span class="text-amber-500">💡</span>
                            <span class="font-bold text-gray-300">老歌友贴心小常识：</span>
                        </p>
                        <p>• <b>1 个半音</b>：就是琴键里的白键和黑键相邻那一点（微调）。</p>
                        <p>• <b>2 个半音（全音）</b>：大约就是您歌词唱高/唱低了<b>一个字音</b>的跨度。</p>
                        <p>• 男声唱女歌建议：降 4 至 5 半音。女声唱男歌建议：升 4 至 5 半音。</p>
                    </div>
                </div>

                <!-- Generate Pitch Accompaniment Action (BIG GLOWING BUTTON) -->
                <button onclick="processPitchShift()" class="mt-5 w-full py-4 bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-500 text-stone-950 font-black rounded-xl text-lg tracking-wide transition active:scale-95 gold-glow-strong flex items-center justify-center space-x-2">
                    <svg class="w-6 h-6 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M14.7 15.3a1 1 0 011.4 1.4l-4 4a1 1 0 01-1.4 0l-4-4a1 1 0 011.4-1.4l3.3 3.29V3a1 1 0 112 0v15.59l3.3-3.3z"></path>
                    </svg>
                    <span>生成并播放变调伴奏</span>
                </button>
            </div>

        </section>

    </main>

    <!-- BIG POPUP MODAL: HOW TO COPY LINK -->
    <div id="help-popup" class="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex items-center justify-center p-4 hidden opacity-0 transition-opacity duration-300">
        <div class="bg-stone-900 border-2 border-amber-400 rounded-3xl p-6 w-full max-w-sm flex flex-col space-y-5 shadow-2xl relative">
            <button onclick="toggleHelpPopup(false)" class="absolute right-4 top-4 w-9 h-9 rounded-full bg-stone-800 text-amber-400 flex items-center justify-center border border-amber-500/30 font-black text-xl active:bg-stone-700">✕</button>
            
            <div class="text-center">
                <h3 class="text-xl font-bold text-amber-300">如何从抖音复制链接？</h3>
                <p class="text-xs text-gray-500 mt-1">简单 3 步，让您瞬间拿到伴奏！</p>
            </div>

            <div class="space-y-4">
                <!-- Step 1 -->
                <div class="flex items-start space-x-3.5">
                    <span class="w-7 h-7 rounded-full bg-amber-500 text-stone-950 font-black flex items-center justify-center shrink-0">1</span>
                    <div>
                        <p class="text-base font-bold text-white">打开手机上的【抖音】</p>
                        <p class="text-xs text-gray-400 mt-0.5">找到您喜欢、想要原歌伴奏的那个视频。</p>
                    </div>
                </div>
                <!-- Step 2 -->
                <div class="flex items-start space-x-3.5">
                    <span class="w-7 h-7 rounded-full bg-amber-500 text-stone-950 font-black flex items-center justify-center shrink-0">2</span>
                    <div>
                        <p class="text-base font-bold text-white">点击右下角的【分享】箭头</p>
                        <p class="text-xs text-gray-400 mt-0.5">在底部弹出的菜单中，找到一个画着圆圈链条的按钮，写着【复制链接】或【分享到微信】。</p>
                    </div>
                </div>
                <!-- Step 3 -->
                <div class="flex items-start space-x-3.5">
                    <span class="w-7 h-7 rounded-full bg-amber-500 text-stone-950 font-black flex items-center justify-center shrink-0">3</span>
                    <div>
                        <p class="text-base font-bold text-white">返回这里，点击【自动粘贴】</p>
                        <p class="text-xs text-gray-400 mt-0.5">系统会自动提取那首歌的背景伴奏。非常省心！</p>
                    </div>
                </div>
            </div>

            <!-- Got it Button -->
            <button onclick="toggleHelpPopup(false)" class="w-full py-3.5 bg-gradient-to-r from-amber-600 to-yellow-500 text-stone-950 font-black rounded-xl text-base tracking-wide gold-glow">
                我知道了，马上去试试！
            </button>
        </div>
    </div>

    <!-- App Footer / Technical Info -->
    <footer class="w-full max-w-md mx-auto py-5 px-4 text-center text-[11px] text-gray-600 border-t border-stone-900 mt-8">
        <p class="font-semibold text-gray-500">中老年合唱团·乐器协会指定伴奏助手</p>
        <p class="mt-1">© 2026 歌伴侣 智能乐感声学实验室 技术支持</p>
    </footer>

    <!-- JavaScript Section with Simulated Tone Synthesizer & Logic Controls -->
    <script>
        // --- GLOBAL APP STATES ---
        let currentScreen = 'page-1';
        let isPlaying = false;
        let selectedSemitone = 1; 
        let pitchDirection = 'raise'; // 'raise' or 'lower'
        let appliedTuning = { direction: 'raise', semitones: 0 }; // Active transposition state
        let simulatedFileName = "伴奏 - 我的祖国 (专业发烧无损伴奏)";
        
        // --- WEB AUDIO API REAL PITCH MODULATOR ---
        // Since we cannot load real copyright audio safely, we build a warm synthesized chord progression 
        // to actually play music and physically transpose frequencies!
        let audioCtx = null;
        let playInterval = null;
        let noteIndex = 0;
        let currentOscillators = [];
        let synthTempo = 120; // BPM

        // Melody chord progression frequencies (C major scale baseline)
        const melodyChords = [
            [261.63, 329.63, 392.00], // C4 major
            [293.66, 349.23, 440.00], // D4 minor
            [329.63, 392.00, 493.88], // E4 minor
            [349.23, 440.00, 523.25], // F4 major
            [392.00, 493.88, 587.33], // G4 major
            [440.00, 554.37, 659.25], // A4 major
            [349.23, 392.00, 587.33]  // G dominant 7th
        ];

        // Init/Toggle Synthesizer Audio
        function initAudioContext() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
        }

        // 核心同步控制：更新播放/暂停按钮的实体图标
        function updatePlayerUI() {
            const playBtnIcon = document.getElementById('play-button-icon');
            if (!playBtnIcon) return;
            if (isPlaying) {
                // 播放中状态：显示“暂停”图标（两条竖线）
                playBtnIcon.innerHTML = `
                    <svg class="w-9 h-9 fill-current" viewBox="0 0 24 24">
                        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                `;
            } else {
                // 暂停中状态：显示“播放”图标（三角形）
                playBtnIcon.innerHTML = `
                    <svg class="w-9 h-9 fill-current" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                `;
            }
        }

        // Play the synthetic loop
        function startSynthPlay() {
            initAudioContext();
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            
            noteIndex = 0;
            // Generate periodic notes mimicking a beautiful high-fidelity golden chime
            playInterval = setInterval(() => {
                playNextSynthChord();
            }, 1000);
            
            isPlaying = true;
            updatePlayerUI();
            startVisualizerAnimation();
        }

        // Stop the synthetic loop
        function stopSynthPlay() {
            if (playInterval) {
                clearInterval(playInterval);
                playInterval = null;
            }
            // Stop any ringing oscillators
            currentOscillators.forEach(osc => {
                try { osc.stop(); } catch(e){}
            });
            currentOscillators = [];
            isPlaying = false;
            updatePlayerUI();
            stopVisualizerAnimation();
        }

        // Synthesize single chord incorporating the active pitch modulation!
        function playNextSynthChord() {
            if (!audioCtx) return;
            
            const chord = melodyChords[noteIndex % melodyChords.length];
            noteIndex++;

            // Calculate the transposition factor
            // Formula: frequency * 2^(semitones / 12)
            let semitoneOffset = appliedTuning.semitones;
            if (appliedTuning.direction === 'lower') {
                semitoneOffset = -semitoneOffset;
            }
            const pitchFactor = Math.pow(2, semitoneOffset / 12);

            // Trigger notes in chord
            chord.forEach(baseFreq => {
                const targetFreq = baseFreq * pitchFactor;
                
                // Create Oscillator
                const osc = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                
                osc.type = 'sine'; // Pure warm sine tones
                osc.frequency.setValueAtTime(targetFreq, audioCtx.currentTime);
                
                // Lowpass filter for smooth analog warmth (like a vinyl record player)
                const filter = audioCtx.createBiquadFilter();
                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(1200, audioCtx.currentTime);

                // Attack Decay Envelope
                gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.15, audioCtx.currentTime + 0.1);
                gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 1.2);

                osc.connect(filter);
                filter.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                
                osc.start();
                osc.stop(audioCtx.currentTime + 1.3);
                
                currentOscillators.push(osc);
                // Garbage collect oscillators
                setTimeout(() => {
                    currentOscillators = currentOscillators.filter(item => item !== osc);
                }, 1400);
            });

            // Handle progress bar update
            simulatedProgress();
        }

        // Simple audio timer simulation
        let currentPlaySec = 0;
        const totalDuration = 180; // 3 mins standard accompaniment duration

        function simulatedProgress() {
            currentPlaySec += 1;
            if (currentPlaySec > totalDuration) {
                currentPlaySec = 0;
                stopSynthPlay();
                return;
            }
            updateProgressBar();
        }

        function updateProgressBar() {
            const percentage = (currentPlaySec / totalDuration) * 100;
            document.getElementById('player-progress-bar').style.width = percentage + '%';
            
            // Format time strings
            const formatTime = (seconds) => {
                const min = Math.floor(seconds / 60);
                const sec = Math.floor(seconds % 60);
                return `${min}:${sec < 10 ? '0' : ''}${sec}`;
            };
            
            document.getElementById('player-time-current').innerText = formatTime(currentPlaySec);
            document.getElementById('player-time-total').innerText = formatTime(totalDuration);
        }

        // Seek position when user taps on the track
        function seekAudio(event) {
            const rect = document.getElementById('slider-track').getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const width = rect.width;
            const relativePosition = clickX / width;
            currentPlaySec = Math.floor(relativePosition * totalDuration);
            updateProgressBar();
            
            showToast(`已为您快进到 ${Math.floor(currentPlaySec / 60)}分${currentPlaySec % 60}秒`);
            
            // If playing, re-sync synthesiser sound trigger instantly
            if (isPlaying) {
                stopSynthPlay();
                startSynthPlay();
            }
        }

        // Jump 5 seconds forward/back
        function skipTime(amount) {
            currentPlaySec += amount;
            if (currentPlaySec < 0) currentPlaySec = 0;
            if (currentPlaySec > totalDuration) currentPlaySec = totalDuration;
            updateProgressBar();
            showToast(amount > 0 ? "快进 5 秒" : "后退 5 秒");
        }

        // Playback Visualizer dynamics switcher
        let animationFrameId = null;
        function startVisualizerAnimation() {
            const bars = document.querySelectorAll('.vu-bar');
            bars.forEach(bar => {
                bar.style.animationPlayState = 'running';
            });
            document.getElementById('vinyl-disc').classList.add('animate-spin');
            // Spin duration logic
            document.getElementById('vinyl-disc').style.animationDuration = '4s';
        }

        function stopVisualizerAnimation() {
            const bars = document.querySelectorAll('.vu-bar');
            bars.forEach(bar => {
                bar.style.animationPlayState = 'paused';
            });
            document.getElementById('vinyl-disc').classList.remove('animate-spin');
        }


        // --- TOAST NOTIFICATIONS ---
        let toastTimeout = null;
        function showToast(message) {
            const toast = document.getElementById('toast');
            const toastText = document.getElementById('toast-text');
            toastText.innerText = message;
            
            toast.classList.remove('opacity-0', 'pointer-events-none');
            toast.classList.add('opacity-100');

            if (toastTimeout) clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => {
                toast.classList.add('opacity-0', 'pointer-events-none');
                toast.classList.remove('opacity-100');
            }, 2500);
        }


        // --- PASTE MECHANISM ---
        function pasteFromClipboard() {
            // Mock read due to security sandbox constraints, but works seamlessly as physical paste helper
            // We read a standard mock link to show the elder how it works
            const mockDouyinText = "7.80 对话框里的精彩 https://v.douyin.com/abc/ 我的祖国大合唱版本伴奏";
            document.getElementById('douyin-input').value = mockDouyinText;
            showToast("已帮您填入抖音链接，请点【开始智能提取】");
        }


        // --- PAGE FLOW SWITCHERS ---
        function triggerFileInput() {
            document.getElementById('audio-file').click();
        }

        function handleFileSelected(event) {
            const file = event.target.files[0];
            if (file) {
                // Ensure size check for elderly notice
                if (file.size > 20 * 1024 * 1024) {
                    showToast("文件超过 20MB 啦，请换一个小一点的文件。");
                    return;
                }
                simulatedFileName = "伴奏 - " + file.name.split('.')[0] + " (原声备份)";
                startProcessAccompaniment();
            }
        }

        // Process Douyin link
        function processDouyin() {
            const inputVal = document.getElementById('douyin-input').value.trim();
            if (!inputVal) {
                showToast("请先在框里贴入您抖音分享的链接喔！");
                return;
            }
            simulatedFileName = "伴奏 - 抖音红歌《" + (extractTitle(inputVal) || "祖国你好") + "》精选伴奏";
            startProcessAccompaniment();
        }

        function extractTitle(text) {
            // Extract some text to make mock sound real
            const match = text.match(/[\u4e00-\u9fa5]{2,6}/);
            return match ? match[0] : null;
        }

        // Simulated AI Cloud Processing for elderly entertainment and trust building
        function startProcessAccompaniment() {
            // Swap display screens
            document.getElementById('page-1').classList.add('hidden');
            document.getElementById('processing-screen').classList.remove('hidden');
            
            let progress = 0;
            const progressLabel = document.getElementById('progress-percent');
            const stepText = document.getElementById('processing-step');
            
            const step1 = document.getElementById('step-1-indicator');
            const step2 = document.getElementById('step-2-indicator');
            const step3 = document.getElementById('step-3-indicator');

            const interval = setInterval(() => {
                progress += Math.floor(Math.random() * 15) + 5;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    
                    // Final transition to results page
                    setTimeout(() => {
                        document.getElementById('processing-screen').classList.add('hidden');
                        document.getElementById('page-2').classList.remove('hidden');
                        currentScreen = 'page-2';
                        
                        // Setup current date validity
                        setupValidityDate();

                        // Set song name
                        document.getElementById('current-song-title').innerText = simulatedFileName;
                        
                        showToast("🎉 您的伴奏制作完成了！");
                        // Automatically start playing synthetic loop
                        startSynthPlay();
                    }, 500);
                }
                
                // Update percentage and steps
                progressLabel.innerText = progress + "%";
                
                if (progress > 30 && progress <= 65) {
                    stepText.innerText = "正在通过AI提取纯伴奏音调...";
                    step1.className = "flex items-center space-x-2 text-xs text-green-400";
                    step2.className = "flex items-center space-x-2 text-xs text-amber-400/80";
                } else if (progress > 65) {
                    stepText.innerText = "伴奏优化完成，正在输出发烧级音频...";
                    step2.className = "flex items-center space-x-2 text-xs text-green-400";
                    step3.className = "flex items-center space-x-2 text-xs text-amber-400/80";
                } else {
                    stepText.innerText = "正在解析并重组云端音频数据...";
                    step1.className = "flex items-center space-x-2 text-xs text-amber-400/80";
                }
            }, 300);
        }

        // Return from results page
        function backToHome() {
            stopSynthPlay();
            currentPlaySec = 0;
            updateProgressBar();
            
            // Back to original parameters
            resetToOriginal();

            document.getElementById('page-2').classList.add('hidden');
            document.getElementById('page-1').classList.remove('hidden');
            currentScreen = 'page-1';
        }


        // --- PITCH CONSOLE LOGICS ---
        function selectPitchDirection(direction) {
            pitchDirection = direction;
            
            const btnRaise = document.getElementById('btn-raise-key');
            const btnLower = document.getElementById('btn-lower-key');

            if (direction === 'raise') {
                btnRaise.className = "py-3 rounded-xl border-2 border-amber-500 bg-amber-500/10 text-amber-300 font-black text-lg flex items-center justify-center space-x-2 transition";
                btnLower.className = "py-3 rounded-xl border border-stone-800 bg-stone-900/60 text-gray-400 font-bold text-lg flex items-center justify-center space-x-2 transition";
            } else {
                btnLower.className = "py-3 rounded-xl border-2 border-amber-500 bg-amber-500/10 text-amber-300 font-black text-lg flex items-center justify-center space-x-2 transition";
                btnRaise.className = "py-3 rounded-xl border border-stone-800 bg-stone-900/60 text-gray-400 font-bold text-lg flex items-center justify-center space-x-2 transition";
            }
            updateTuningLabel();
        }

        function setSemitone(num) {
            selectedSemitone = num;
            
            // Style active semitone button
            const btns = document.querySelectorAll('.semitone-btn');
            btns.forEach((btn, index) => {
                if (index === num - 1) {
                    btn.className = "semitone-btn py-3 rounded-xl text-stone-950 bg-amber-500 border border-amber-300 font-black text-lg transition active:scale-95 shadow-md";
                } else {
                    btn.className = "semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95";
                }
            });
            updateTuningLabel();
        }

        function updateTuningLabel() {
            const stepsText = document.getElementById('current-steps-text');
            const dirChinese = pitchDirection === 'raise' ? '调高' : '调低';
            stepsText.innerText = `已选 ${dirChinese} ${selectedSemitone} 个半音`;
        }

        // Apply shift values to synthesizer
        function processPitchShift() {
            appliedTuning.direction = pitchDirection;
            appliedTuning.semitones = selectedSemitone;

            // Re-render display text
            const displayEl = document.getElementById('current-key-display');
            const iconEl = document.getElementById('tuning-badge-icon');
            
            const dirChinese = appliedTuning.direction === 'raise' ? '升高' : '降低';
            displayEl.innerText = `当前版本：已${dirChinese} ${appliedTuning.semitones} 个半音`;
            iconEl.innerText = appliedTuning.direction === 'raise' ? '📈' : '📉';

            showToast(`⚡ 已成功调制为：[${dirChinese}${appliedTuning.semitones}个半音]！正在高品质播放...`);

            // If not playing, trigger instantly. If already playing, synth naturally updates pitch in real-time.
            if (!isPlaying) {
                startSynthPlay();
            } else {
                // Flash visualizer animation to simulate processor recalculating
                stopVisualizerAnimation();
                setTimeout(() => {
                    startVisualizerAnimation();
                }, 150);
            }
        }

        // Reset to original baseline key
        function resetToOriginal() {
            selectedSemitone = 0;
            appliedTuning.semitones = 0;
            appliedTuning.direction = 'raise';

            // Reset UI buttons
            const btns = document.querySelectorAll('.semitone-btn');
            btns.forEach(btn => {
                btn.className = "semitone-btn py-3 rounded-xl text-gray-300 bg-stone-900 border border-stone-800 font-bold text-lg transition active:scale-95";
            });

            document.getElementById('current-key-display').innerText = `当前版本：原调 (未作修改)`;
            document.getElementById('tuning-badge-icon').innerText = '🎵';
            document.getElementById('current-steps-text').innerText = `已调 0 个半音`;

            showToast("🔄 已成功切回到歌曲初始原调");
        }

        // Play/Pause control mapping
        function toggleAudio() {
            if (isPlaying) {
                stopSynthPlay();
                showToast("伴奏已暂停");
            } else {
                startSynthPlay();
                showToast("正在播放高质量纯伴奏");
            }
        }


        // --- HELPERS / DIALOGS ---
        function toggleHelpPopup(show) {
            const modal = document.getElementById('help-popup');
            if (show) {
                modal.classList.remove('hidden');
                setTimeout(() => { modal.classList.remove('opacity-0'); }, 10);
            } else {
                modal.classList.add('opacity-0');
                setTimeout(() => { modal.classList.add('hidden'); }, 300);
            }
        }

        // Simulated Download Action
        function simulateDownload() {
            showToast("💾 正在将高品质 MP3 伴奏文件打包下载到手机系统...");
            setTimeout(() => {
                showToast("✅ 下载完成！您可以直接导入唱吧或在微信里播放啦。");
            }, 2500);
        }

        // Simulated Copy Web Link Action
        function copyAccompanimentLink() {
            // Using standard compatibility mode for sharing
            const dummyInput = document.createElement("input");
            document.body.appendChild(dummyInput);
            dummyInput.value = `http://gebanlv.com/download/accompaniment_id_8897_${appliedTuning.direction}_${appliedTuning.semitones}`;
            dummyInput.select();
            document.execCommand('copy');
            document.body.removeChild(dummyInput);

            showToast("🔗 伴奏专属提取网址已自动复制！快去微信长按【粘贴】发给您的合唱团团友或老师吧！");
        }

        // Formulate relative dynamic date based on system clock
        function setupValidityDate() {
            const dateSpan = document.getElementById('expire-date');
            const today = new Date();
            // Set expire date to exactly 7 days from now
            today.setDate(today.getDate() + 7);
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            dateSpan.innerText = `${year}.${month}.${day}`;
        }

        // Start initialization block
        window.onload = function() {
            // Check that visuals are responsive inside viewports
            updateProgressBar();
            // Default select semitone 1
            setSemitone(1);
        };
    </script>
</body>
</html>