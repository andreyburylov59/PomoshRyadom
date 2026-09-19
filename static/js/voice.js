/**
 * Голосовой ввод через Web Speech API
 * Для использования в форме создания задания
 */

class VoiceInput {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.transcript = '';
        this.initRecognition();
    }
    
    /**
     * Инициализация Web Speech API
     */
    initRecognition() {
        // Проверка поддержки браузером
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Web Speech API не поддерживается этим браузером');
            this.showError('Ваш браузер не поддерживает голосовой ввод. Попробуйте Chrome.');
            return;
        }
        
        // Создание объекта распознавания
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Настройки
        this.recognition.lang = 'ru-RU'; // Русский язык
        this.recognition.continuous = true; // Непрерывное распознавание
        this.recognition.interimResults = true; // Промежуточные результаты
        this.recognition.maxAlternatives = 1;
        
        // События
        this.recognition.onstart = () => this.onStart();
        this.recognition.onresult = (event) => this.onResult(event);
        this.recognition.onerror = (event) => this.onError(event);
        this.recognition.onend = () => this.onEnd();
    }
    
    /**
     * Начало записи
     */
    startListening() {
        if (!this.recognition) {
            this.showError('Голосовой ввод недоступен');
            return;
        }
        
        if (this.isListening) {
            return;
        }
        
        try {
            this.transcript = '';
            this.recognition.start();
        } catch (error) {
            console.error('Ошибка при запуске распознавания:', error);
            this.showError('Не удалось запустить распознавание речи');
        }
    }
    
    /**
     * Остановка записи
     */
    stopListening() {
        if (!this.recognition || !this.isListening) {
            return;
        }
        
        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Ошибка при остановке распознавания:', error);
        }
    }
    
    /**
     * Обработчик начала записи
     */
    onStart() {
        this.isListening = true;
        this.updateUI(true);
        this.showStatus('Говорите... Микрофон включен');
    }
    
    /**
     * Обработчик результатов распознавания
     */
    onResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        // Обработка результатов
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Обновление полной транскрипции
        if (finalTranscript) {
            this.transcript += finalTranscript;
            this.updateTranscriptDisplay();
        }
        
        // Показ промежуточных результатов
        if (interimTranscript) {
            this.showStatus('Распознаю: ' + interimTranscript);
        }
    }
    
    /**
     * Обработчик ошибок
     */
    onError(event) {
        console.error('Ошибка распознавания:', event.error);
        
        let errorMessage = 'Произошла ошибка при распознавании речи';
        
        switch (event.error) {
            case 'no-speech':
                errorMessage = 'Речь не обнаружена. Попробуйте ещё раз.';
                break;
            case 'audio-capture':
                errorMessage = 'Микрофон недоступен. Проверьте настройки.';
                break;
            case 'not-allowed':
                errorMessage = 'Доступ к микрофону запрещён. Разрешите доступ в настройках браузера.';
                break;
            case 'network':
                errorMessage = 'Ошибка сети. Проверьте подключение к интернету.';
                break;
        }
        
        this.showError(errorMessage);
        this.isListening = false;
        this.updateUI(false);
    }
    
    /**
     * Обработчик окончания записи
     */
    onEnd() {
        this.isListening = false;
        this.updateUI(false);
        
        if (this.transcript.trim()) {
            this.showStatus('Распознавание завершено. Обрабатываю текст...');
            this.processTranscript();
        } else {
            this.showStatus('Речь не распознана. Попробуйте ещё раз.');
        }
    }
    
    /**
     * Обработка распознанного текста и заполнение формы
     */
    processTranscript() {
        const text = this.transcript.trim().toLowerCase();
        
        // Очистка текста
        const cleanText = this.transcript.trim();
        
        // Попытка извлечь информацию из текста
        const extractedData = this.extractTaskInfo(cleanText);
        
        // Заполнение полей формы
        this.fillFormFields(extractedData);
        
        this.showSuccess('Форма заполнена! Проверьте и отредактируйте данные.');
    }
    
    /**
     * Извлечение информации о задании из текста
     */
    extractTaskInfo(text) {
        const data = {
            title: '',
            description: text,
            category: '',
            price: '',
            address: '',
            district: '',
            urgency: 'планово'
        };
        
        const lowerText = text.toLowerCase();
        
        // Извлечение цены
        const pricePatterns = [
            /(\d+)\s*(?:рубл|₽|руб)/gi,
            /за\s*(\d+)/gi,
            /цена\s*(\d+)/gi,
            /плачу\s*(\d+)/gi,
            /заплачу\s*(\d+)/gi
        ];
        
        for (const pattern of pricePatterns) {
            const match = text.match(pattern);
            if (match) {
                const price = match[0].match(/\d+/);
                if (price) {
                    data.price = price[0];
                    break;
                }
            }
        }
        
        // Определение категории по ключевым словам
        const categories = {
            'уборка': ['убор', 'помыть', 'почистить', 'навести порядок', 'генеральн', 'вымыть'],
            'доставка': ['доставить', 'привезти', 'купить и принести', 'привозить', 'доставк'],
            'сантехника': ['кран', 'трубу', 'унитаз', 'раковин', 'сантехник', 'течёт', 'протека', 'смеситель'],
            'электрика': ['розетк', 'свет', 'лампочк', 'проводк', 'электрик', 'выключатель', 'люстр'],
            'мастер': ['починить', 'отремонтировать', 'исправить', 'мастер'],
            'сборка мебели': ['собрать', 'мебель', 'шкаф', 'стол', 'икеа', 'ikea', 'сборк'],
            'компьютерная помощь': ['компьютер', 'ноутбук', 'wi-fi', 'вай-фай', 'интернет', 'роутер', 'настроить', 'виндовс', 'windows'],
            'переезд': ['переезд', 'перевезти', 'грузчик', 'вывезти', 'транспорт'],
            'няня': ['няня', 'посидеть с ребенком', 'детьми', 'присмотреть за ребенком'],
            'репетитор': ['репетитор', 'научить', 'позаниматься', 'урок', 'подготовк']
        };
        
        for (const [category, keywords] of Object.entries(categories)) {
            for (const keyword of keywords) {
                if (lowerText.includes(keyword)) {
                    data.category = category;
                    break;
                }
            }
            if (data.category) break;
        }
        
        // Определение срочности
        if (lowerText.includes('срочно') || lowerText.includes('быстро') || lowerText.includes('сегодня') || lowerText.includes('сейчас')) {
            data.urgency = 'срочно';
        }
        
        // Извлечение адреса
        const addressPatterns = [
            /(?:по адресу|адрес)\s*([^.!?]+)/gi,
            /(?:на|по)\s+улиц[еа]\s+([^.!?]+)/gi,
            /(?:проспект|пр\.|пр-т)\s+([^.!?]+)/gi
        ];
        
        for (const pattern of addressPatterns) {
            const match = text.match(pattern);
            if (match && match[1]) {
                data.address = match[1].trim();
                break;
            }
        }
        
        // Извлечение района
        const districts = [
            'центральный', 'северный', 'южный', 'западный', 'восточный',
            'ленинский', 'октябрьский', 'советский', 'железнодорожный', 'заречный'
        ];
        
        for (const district of districts) {
            if (lowerText.includes(district)) {
                data.district = district.charAt(0).toUpperCase() + district.slice(1);
                break;
            }
        }
        
        // Генерация заголовка на основе категории и ключевых слов
        if (data.category) {
            const firstSentence = text.split(/[.!?]/)[0];
            data.title = firstSentence.substring(0, 100);
        } else {
            data.title = text.substring(0, 100);
        }
        
        // Если заголовок слишком длинный, укорачиваем
        if (data.title.length > 80) {
            data.title = data.title.substring(0, 77) + '...';
        }
        
        return data;
    }
    
    /**
     * Заполнение полей формы
     */
    fillFormFields(data) {
        // Заголовок
        const titleField = document.getElementById('title');
        if (titleField && data.title) {
            titleField.value = data.title;
        }
        
        // Описание
        const descriptionField = document.getElementById('description');
        if (descriptionField && data.description) {
            descriptionField.value = data.description;
        }
        
        // Категория
        const categoryField = document.getElementById('category');
        if (categoryField && data.category) {
            categoryField.value = data.category;
        }
        
        // Цена
        const priceField = document.getElementById('price');
        if (priceField && data.price) {
            priceField.value = data.price;
        }
        
        // Адрес
        const addressField = document.getElementById('address');
        if (addressField && data.address) {
            addressField.value = data.address;
        }
        
        // Район
        const districtField = document.getElementById('district');
        if (districtField && data.district) {
            districtField.value = data.district;
        }
        
        // Срочность
        if (data.urgency === 'срочно') {
            const urgentRadio = document.getElementById('urgency_urgent');
            if (urgentRadio) {
                urgentRadio.checked = true;
            }
        }
    }
    
    /**
     * Обновление отображения транскрипции
     */
    updateTranscriptDisplay() {
        const display = document.getElementById('voice-transcript');
        if (display) {
            display.textContent = this.transcript;
        }
    }
    
    /**
     * Обновление UI кнопки
     */
    updateUI(isListening) {
        const button = document.getElementById('voice-button');
        const icon = document.getElementById('voice-icon');
        const text = document.getElementById('voice-text');
        
        if (button) {
            if (isListening) {
                button.classList.add('listening');
                if (icon) icon.textContent = '⏹️';
                if (text) text.textContent = 'Остановить запись';
            } else {
                button.classList.remove('listening');
                if (icon) icon.textContent = '🎤';
                if (text) text.textContent = 'Начать голосовой ввод';
            }
        }
    }
    
    /**
     * Показать статус
     */
    showStatus(message) {
        const statusEl = document.getElementById('voice-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = 'voice-status';
        }
    }
    
    /**
     * Показать успех
     */
    showSuccess(message) {
        const statusEl = document.getElementById('voice-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = 'voice-status success';
        }
    }
    
    /**
     * Показать ошибку
     */
    showError(message) {
        const statusEl = document.getElementById('voice-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = 'voice-status error';
        }
    }
    
    /**
     * Переключение записи
     */
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
}

// Глобальная инициализация
let voiceInput = null;

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация только если есть кнопка голосового ввода
    const voiceButton = document.getElementById('voice-button');
    if (voiceButton) {
        voiceInput = new VoiceInput();
        
        // Обработчик кнопки
        voiceButton.addEventListener('click', function() {
            voiceInput.toggleListening();
        });
    }
});
