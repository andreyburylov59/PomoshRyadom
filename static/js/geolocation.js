/**
 * Геолокация через Geolocation API
 * Определение района и фильтрация заданий по расстоянию
 */

class GeoLocation {
    constructor() {
        this.currentPosition = null;
        this.watchId = null;
        this.isSupported = 'geolocation' in navigator;
    }
    
    /**
     * Проверка поддержки геолокации
     */
    checkSupport() {
        if (!this.isSupported) {
            console.warn('Geolocation API не поддерживается этим браузером');
            return false;
        }
        return true;
    }
    
    /**
     * Получить текущее местоположение
     */
    getCurrentPosition(successCallback, errorCallback) {
        if (!this.checkSupport()) {
            if (errorCallback) {
                errorCallback({
                    code: -1,
                    message: 'Геолокация не поддерживается вашим браузером'
                });
            }
            return;
        }
        
        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 минут
        };
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.currentPosition = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
                
                if (successCallback) {
                    successCallback(this.currentPosition);
                }
            },
            (error) => {
                console.error('Ошибка геолокации:', error);
                if (errorCallback) {
                    errorCallback(this.handleError(error));
                }
            },
            options
        );
    }
    
    /**
     * Обработка ошибок геолокации
     */
    handleError(error) {
        let message = 'Не удалось определить местоположение';
        
        switch (error.code) {
            case error.PERMISSION_DENIED:
                message = 'Вы запретили доступ к геолокации. Разрешите доступ в настройках браузера.';
                break;
            case error.POSITION_UNAVAILABLE:
                message = 'Информация о местоположении недоступна.';
                break;
            case error.TIMEOUT:
                message = 'Превышено время ожидания. Попробуйте ещё раз.';
                break;
        }
        
        return {
            code: error.code,
            message: message
        };
    }
    
    /**
     * Вычислить расстояние между двумя точками (формула Haversine)
     * @param {number} lat1 - широта первой точки
     * @param {number} lon1 - долгота первой точки
     * @param {number} lat2 - широта второй точки
     * @param {number} lon2 - долгота второй точки
     * @returns {number} - расстояние в километрах
     */
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Радиус Земли в километрах
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c;
        
        return distance;
    }
    
    /**
     * Конвертация градусов в радианы
     */
    toRad(degrees) {
        return degrees * Math.PI / 180;
    }
    
    /**
     * Определить район по координатам
     * (Упрощённый алгоритм - в реальности нужна база координат районов)
     */
    getDistrictByCoordinates(latitude, longitude) {
        // Координаты центров районов (примерные, для демо)
        const districts = {
            'Центральный': { lat: 55.7558, lon: 37.6173 },
            'Северный': { lat: 55.8558, lon: 37.6173 },
            'Южный': { lat: 55.6558, lon: 37.6173 },
            'Западный': { lat: 55.7558, lon: 37.5173 },
            'Восточный': { lat: 55.7558, lon: 37.7173 },
            'Ленинский': { lat: 55.7058, lon: 37.6673 },
            'Октябрьский': { lat: 55.8058, lon: 37.5673 },
            'Советский': { lat: 55.7858, lon: 37.6873 },
            'Железнодорожный': { lat: 55.7358, lon: 37.7373 },
            'Заречный': { lat: 55.7258, lon: 37.5873 }
        };
        
        let nearestDistrict = null;
        let minDistance = Infinity;
        
        // Находим ближайший район
        for (const [name, coords] of Object.entries(districts)) {
            const distance = this.calculateDistance(
                latitude,
                longitude,
                coords.lat,
                coords.lon
            );
            
            if (distance < minDistance) {
                minDistance = distance;
                nearestDistrict = name;
            }
        }
        
        return {
            district: nearestDistrict,
            distance: minDistance.toFixed(2)
        };
    }
    
    /**
     * Форматирование расстояния для отображения
     */
    formatDistance(km) {
        if (km < 1) {
            return Math.round(km * 1000) + ' м';
        }
        return km.toFixed(1) + ' км';
    }
}

// Глобальный экземпляр
let geoLocation = null;

/**
 * Определить район автоматически
 */
function autoDetectDistrict() {
    const button = document.getElementById('detect-location-btn');
    const districtField = document.getElementById('district');
    const statusEl = document.getElementById('location-status');
    
    if (!geoLocation) {
        geoLocation = new GeoLocation();
    }
    
    // Показываем индикатор загрузки
    if (button) {
        button.disabled = true;
        button.textContent = 'Определяем...';
    }
    
    if (statusEl) {
        statusEl.textContent = 'Определяем ваше местоположение...';
        statusEl.className = 'location-status loading';
    }
    
    // Получаем координаты
    geoLocation.getCurrentPosition(
        (position) => {
            // Определяем район
            const result = geoLocation.getDistrictByCoordinates(
                position.latitude,
                position.longitude
            );
            
            // Заполняем поле района
            if (districtField) {
                districtField.value = result.district;
            }
            
            // Сохраняем координаты в скрытые поля
            const latField = document.getElementById('latitude');
            const lonField = document.getElementById('longitude');
            if (latField) latField.value = position.latitude;
            if (lonField) lonField.value = position.longitude;
            
            // Показываем успех
            if (statusEl) {
                statusEl.textContent = `✓ Определён район: ${result.district} (точность ${Math.round(position.accuracy)}м)`;
                statusEl.className = 'location-status success';
            }
            
            if (button) {
                button.disabled = false;
                button.textContent = '📍 Определить район';
            }
        },
        (error) => {
            // Показываем ошибку
            if (statusEl) {
                statusEl.textContent = error.message;
                statusEl.className = 'location-status error';
            }
            
            if (button) {
                button.disabled = false;
                button.textContent = '📍 Определить район';
            }
        }
    );
}

/**
 * Фильтрация заданий по расстоянию
 */
function filterTasksByDistance(maxDistance = 3) {
    if (!geoLocation) {
        geoLocation = new GeoLocation();
    }
    
    const statusEl = document.getElementById('distance-filter-status');
    
    if (statusEl) {
        statusEl.textContent = 'Определяем ваше местоположение...';
        statusEl.className = 'filter-status loading';
    }
    
    geoLocation.getCurrentPosition(
        (position) => {
            // Получаем все карточки заданий
            const taskCards = document.querySelectorAll('.task-card');
            let hiddenCount = 0;
            let shownCount = 0;
            
            taskCards.forEach((card) => {
                const lat = parseFloat(card.dataset.latitude);
                const lon = parseFloat(card.dataset.longitude);
                
                if (lat && lon) {
                    const distance = geoLocation.calculateDistance(
                        position.latitude,
                        position.longitude,
                        lat,
                        lon
                    );
                    
                    // Добавляем badge с расстоянием
                    let distanceBadge = card.querySelector('.distance-badge');
                    if (!distanceBadge) {
                        distanceBadge = document.createElement('span');
                        distanceBadge.className = 'task-badge distance-badge';
                        const metaDiv = card.querySelector('.task-meta');
                        if (metaDiv) {
                            metaDiv.appendChild(distanceBadge);
                        }
                    }
                    distanceBadge.textContent = geoLocation.formatDistance(distance);
                    
                    // Фильтруем по расстоянию
                    if (distance <= maxDistance) {
                        card.style.display = '';
                        shownCount++;
                    } else {
                        card.style.display = 'none';
                        hiddenCount++;
                    }
                }
            });
            
            // Обновляем статус
            if (statusEl) {
                statusEl.textContent = `✓ Показано ${shownCount} заданий в радиусе ${maxDistance} км`;
                statusEl.className = 'filter-status success';
            }
            
            // Обновляем счётчик
            const countEl = document.querySelector('.tasks-count');
            if (countEl) {
                countEl.textContent = `Найдено заданий: ${shownCount}`;
            }
        },
        (error) => {
            if (statusEl) {
                statusEl.textContent = error.message;
                statusEl.className = 'filter-status error';
            }
        }
    );
}

/**
 * Сброс фильтра по расстоянию
 */
function resetDistanceFilter() {
    const taskCards = document.querySelectorAll('.task-card');
    let count = 0;
    
    taskCards.forEach((card) => {
        card.style.display = '';
        
        // Удаляем badge с расстоянием
        const distanceBadge = card.querySelector('.distance-badge');
        if (distanceBadge) {
            distanceBadge.remove();
        }
        
        count++;
    });
    
    // Обновляем счётчик
    const countEl = document.querySelector('.tasks-count');
    if (countEl) {
        countEl.textContent = `Найдено заданий: ${count}`;
    }
    
    // Очищаем статус
    const statusEl = document.getElementById('distance-filter-status');
    if (statusEl) {
        statusEl.textContent = '';
        statusEl.className = 'filter-status';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    geoLocation = new GeoLocation();
    
    // Кнопка автоопределения района
    const detectButton = document.getElementById('detect-location-btn');
    if (detectButton) {
        detectButton.addEventListener('click', autoDetectDistrict);
    }
    
    // Кнопка фильтра по расстоянию
    const filterButton = document.getElementById('filter-by-distance-btn');
    if (filterButton) {
        filterButton.addEventListener('click', function() {
            const maxDistance = parseFloat(document.getElementById('max-distance')?.value || 3);
            filterTasksByDistance(maxDistance);
        });
    }
    
    // Кнопка сброса фильтра
    const resetButton = document.getElementById('reset-distance-filter-btn');
    if (resetButton) {
        resetButton.addEventListener('click', resetDistanceFilter);
    }
});
