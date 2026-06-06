// static/js/ar_handler.js
// AR Handler for Elderly Companion - Manages 3D models, interactions, and AR features

class ARCompanion {
    constructor() {
        this.modelViewer = null;
        this.currentModel = null;
        this.isARMode = false;
        this.interactionCount = 0;
        this.lastInteractionTime = null;
        this.availableModels = {
            companion: '/static/models/companion.glb',
            friend: 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/DamagedHelmet/glTF/DamagedHelmet.gltf',
            garden: 'https://threejs.org/examples/models/gltf/Flamingo.gltf',
            nature: 'https://threejs.org/examples/models/gltf/Parrot.glb'
        };
    }

    /**
     * Initialize the AR companion
     * @param {string} containerId - ID of the container element
     */
    init(containerId = 'ar-container') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('AR container not found');
            return;
        }

        // Create model-viewer element
        this.modelViewer = document.createElement('model-viewer');
        this.modelViewer.id = 'companion-viewer';
        this.modelViewer.setAttribute('src', this.availableModels.companion);
        this.modelViewer.setAttribute('ar', '');
        this.modelViewer.setAttribute('ar-modes', 'webxr scene-viewer quick-look');
        this.modelViewer.setAttribute('camera-controls', '');
        this.modelViewer.setAttribute('auto-rotate', '');
        this.modelViewer.setAttribute('style', 'width:100%; height:100%; background: #2a2a2a;');
        
        // Add AR button
        const arButton = document.createElement('button');
        arButton.setAttribute('slot', 'ar-button');
        arButton.textContent = '🕶️ View in AR';
        arButton.style.cssText = 'background: #DAA520; border: none; color: white; padding: 10px 20px; border-radius: 30px; cursor: pointer;';
        arButton.onclick = () => this.enterARMode();
        this.modelViewer.appendChild(arButton);
        
        container.innerHTML = '';
        container.appendChild(this.modelViewer);
        
        // Add event listeners
        this.modelViewer.addEventListener('load', () => this.onModelLoaded());
        this.modelViewer.addEventListener('error', (e) => this.onModelError(e));
        
        // Start companion animation
        this.startCompanionAnimation();
        
        // Log initialization
        this.logInteraction('ar_init', 0);
        
        console.log('✅ AR Companion initialized successfully');
    }

    /**
     * Called when 3D model is loaded
     */
    onModelLoaded() {
        console.log('🎨 3D model loaded successfully');
        this.showMessage('مرحباً! أنا صديقك الافتراضي. كيف يمكنني مساعدتك اليوم؟');
        this.logInteraction('model_loaded', 0);
    }

    /**
     * Called when model loading fails
     */
    onModelError(error) {
        console.error('❌ Failed to load 3D model:', error);
        this.showMessage('عذراً، حدث خطأ في تحميل الصديق الافتراضي. يرجى تحديث الصفحة.');
    }

    /**
     * Enter Augmented Reality mode
     */
    enterARMode() {
        if (this.modelViewer && this.modelViewer.canActivateAR) {
            this.modelViewer.activateAR();
            this.isARMode = true;
            this.logInteraction('ar_mode_entered', 0);
            this.showMessage('🎉 أنت الآن في وضع الواقع المعزز! يمكنك التفاعل مع صديقك الافتراضي.');
        } else {
            alert('الواقع المعزز غير مدعوم على هذا الجهاز. يرجى استخدام متصفح Chrome على هاتف Android أو Safari على iPhone.');
        }
    }

    /**
     * Change the 3D model
     * @param {string} modelType - Type of model to load ('companion', 'friend', 'garden', 'nature')
     */
    changeModel(modelType) {
        if (!this.availableModels[modelType]) {
            console.error('Unknown model type:', modelType);
            return;
        }
        
        this.modelViewer.setAttribute('src', this.availableModels[modelType]);
        this.logInteraction('model_changed', 0, {model_type: modelType});
        this.showMessage(`تم تغيير البيئة إلى ${this.getModelName(modelType)}`);
    }

    /**
     * Get display name for model type
     */
    getModelName(modelType) {
        const names = {
            companion: 'الصديق الافتراضي',
            friend: 'الرفيق المرح',
            garden: 'الحديقة الهادئة',
            nature: 'الطبيعة الخلابة'
        };
        return names[modelType] || modelType;
    }

    /**
     * Start companion animation (simulated speech bubbles)
     */
    startCompanionAnimation() {
        setInterval(() => {
            if (!this.isARMode && Math.random() > 0.7) {
                const randomGreetings = [
                    'كيف تشعر اليوم؟',
                    'هل تريد التحدث مع العائلة؟',
                    'لدي لعبة جديدة لك!',
                    'هل تحتاج أي مساعدة؟',
                    'أنا هنا لأسمعك'
                ];
                const randomGreeting = randomGreetings[Math.floor(Math.random() * randomGreetings.length)];
                this.showMessage(randomGreeting, 3000);
            }
        }, 15000); // Every 15 seconds
    }

    /**
     * Show a message bubble from the companion
     * @param {string} message - Message to display
     * @param {number} duration - Duration in milliseconds
     */
    showMessage(message, duration = 5000) {
        // Find or create message bubble
        let bubble = document.getElementById('companion-message-bubble');
        if (!bubble) {
            bubble = document.createElement('div');
            bubble.id = 'companion-message-bubble';
            bubble.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #DAA520, #B8860B);
                color: white;
                padding: 12px 20px;
                border-radius: 50px;
                font-size: 16px;
                font-weight: bold;
                z-index: 1000;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                animation: fadeInUp 0.3s ease;
                text-align: center;
                max-width: 80%;
                white-space: nowrap;
            `;
            document.body.appendChild(bubble);
            
            // Add animation style
            if (!document.querySelector('#ar-animation-style')) {
                const style = document.createElement('style');
                style.id = 'ar-animation-style';
                style.textContent = `
                    @keyframes fadeInUp {
                        from {
                            opacity: 0;
                            transform: translateX(-50%) translateY(20px);
                        }
                        to {
                            opacity: 1;
                            transform: translateX(-50%) translateY(0);
                        }
                    }
                    @keyframes fadeOutDown {
                        from {
                            opacity: 1;
                            transform: translateX(-50%) translateY(0);
                        }
                        to {
                            opacity: 0;
                            transform: translateX(-50%) translateY(20px);
                        }
                    }
                `;
                document.head.appendChild(style);
            }
        }
        
        bubble.textContent = message;
        bubble.style.display = 'block';
        bubble.style.animation = 'fadeInUp 0.3s ease';
        
        // Auto-hide after duration
        setTimeout(() => {
            if (bubble) {
                bubble.style.animation = 'fadeOutDown 0.3s ease';
                setTimeout(() => {
                    if (bubble) bubble.style.display = 'none';
                }, 300);
            }
        }, duration);
        
        // Log interaction
        this.logInteraction('message_shown', 0, {message: message.substring(0, 50)});
    }

    /**
     * Handle voice input (Web Speech API)
     */
    startVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('التعرف على الصوت غير مدعوم في متصفحك. يرجى استخدام Chrome أو Edge.');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'ar-SA'; // Arabic
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        // Show listening indicator
        this.showMessage('🎤 جاري الاستماع... تحدث الآن', 2000);
        
        recognition.start();
        
        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            this.processVoiceCommand(speechResult);
        };
        
        recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.showMessage('عذراً، لم أتمكن من فهمك. يرجى المحاولة مرة أخرى.');
        };
    }

    /**
     * Process voice command
     * @param {string} command - Recognized speech text
     */
    processVoiceCommand(command) {
        console.log('Voice command:', command);
        this.logInteraction('voice_command', 0, {command: command});
        
        const lowerCommand = command.toLowerCase();
        
        if (lowerCommand.includes('لعبة') || lowerCommand.includes('game')) {
            this.showMessage('🎮 رائع! هل تريد لعب لعبة تنشيط الذاكرة؟');
            this.triggerGameSuggestion();
        } else if (lowerCommand.includes('عائلة') || lowerCommand.includes('family')) {
            this.showMessage('👨‍👩‍👧‍👦 سأتصل بأحد أفراد العائلة. لحظة من فضلك...');
            this.triggerFamilyCall();
        } else if (lowerCommand.includes('استرخاء') || lowerCommand.includes('meditate')) {
            this.showMessage('🧘 دعنا نأخذ نفساً عميقاً معاً... شهيق... زفير...');
            this.triggerMeditation();
        } else if (lowerCommand.includes('مساعد') || lowerCommand.includes('help')) {
            this.showMessage('يمكنك أن تطلب مني: تشغيل لعبة، الاتصال بالعائلة، أو جلسة استرخاء');
        } else {
            this.showMessage('شكراً لك على التحدث معي. كيف يمكنني مساعدتك اليوم؟');
        }
    }

    /**
     * Trigger game suggestion
     */
    triggerGameSuggestion() {
        const gameButton = document.querySelector('button[onclick*="game"]');
        if (gameButton) {
            gameButton.click();
        } else {
            this.showMessage('يمكنك لعب لعبة تنشيط الذاكرة من القائمة الرئيسية.');
        }
        this.logInteraction('game_triggered', 0);
    }

    /**
     * Trigger family call
     */
    triggerFamilyCall() {
        fetch('/api/family-members')
            .then(res => res.json())
            .then(family => {
                if (family && family.length > 0) {
                    const familyNames = family.map(m => m.name).join('، ');
                    this.showMessage(`يمكنك الاتصال بـ: ${familyNames}. هل تريد مساعدتي في الاتصال؟`);
                } else {
                    this.showMessage('لم يتم إضافة أفراد عائلة بعد. يمكنك إضافتهم من إعدادات الملف الشخصي.');
                }
            })
            .catch(() => {
                this.showMessage('حدث خطأ في جلب جهات الاتصال. يرجى المحاولة لاحقاً.');
            });
        this.logInteraction('family_call_triggered', 0);
    }

    /**
     * Trigger meditation session
     */
    triggerMeditation() {
        this.showMessage('🧘 خذ نفساً عميقاً... تخيل مكاناً هادئاً... أنت بخير...');
        setTimeout(() => {
            this.showMessage('🌟 كيف تشعر الآن؟ أتمنى أن تكون أكثر استرخاءً.');
        }, 5000);
        this.logInteraction('meditation_triggered', 5);
    }

    /**
     * Log interaction to server
     * @param {string} type - Interaction type
     * @param {number} duration - Duration in seconds
     * @param {Object} metadata - Additional metadata
     */
    logInteraction(type, duration, metadata = {}) {
        this.interactionCount++;
        this.lastInteractionTime = Date.now();
        
        fetch('/api/log-interaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: type,
                duration: duration,
                completion: 100,
                metadata: metadata
            })
        }).catch(error => console.error('Failed to log interaction:', error));
    }

    /**
     * Get companion statistics
     */
    getStats() {
        return {
            interactionCount: this.interactionCount,
            lastInteractionTime: this.lastInteractionTime,
            isARMode: this.isARMode,
            currentModel: this.modelViewer?.getAttribute('src')
        };
    }
}

// Initialize AR Companion when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.arCompanion = new ARCompanion();
    
    // Auto-initialize if ar-container exists
    if (document.getElementById('ar-container')) {
        window.arCompanion.init();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ARCompanion;
}
