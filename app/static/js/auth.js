// Класс для управления авторизацией
class AuthService {
    constructor() {
        this.accessToken = null;
        this.refreshPromise = null; // Для предотвращения множественных обновлений
    }

    // Сохранить access token (в память, не в localStorage!)
    setAccessToken(token) {
        this.accessToken = token;
    }

    // Получить access token
    getAccessToken() {
        return this.accessToken;
    }

    // Проверить, авторизован ли пользователь
    isAuthenticated() {
        return !!this.accessToken;
    }

    // Логин
    async login(username, password) {
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password }),
                credentials: 'include' // Важно! Для работы с cookies
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            // Сохраняем access token в память
            this.setAccessToken(data.access_token);
            
            // Сохраняем информацию о пользователе (опционально)
            localStorage.setItem('user', JSON.stringify({
                username: username,
                loginTime: Date.now()
            }));
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    // Регистрация
    async register(username, password) {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return await response.json();
    }

    // Обновление access token
    async refreshToken() {
        // Если уже идет обновление, возвращаем тот же Promise
        if (this.refreshPromise) {
            return this.refreshPromise;
        }

        this.refreshPromise = fetch('/auth/refresh', {
            method: 'POST',
            credentials: 'include' // Важно! Отправляем cookie с refresh token
        })
        .then(async response => {
            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }
            const data = await response.json();
            this.setAccessToken(data.access_token);
            return data.access_token;
        })
        .finally(() => {
            this.refreshPromise = null;
        });

        return this.refreshPromise;
    }

    // Выход
    async logout() {
        await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        this.accessToken = null;
        localStorage.removeItem('user');
        
        // Перенаправление на страницу логина
        window.location.href = '/login.html';
    }

    // Получение текущего пользователя
    async getCurrentUser() {
        const response = await this.fetchWithAuth('/auth/me');
        if (!response.ok) {
            return null;
        }
        return await response.json();
    }

    // Универсальный fetch с автоматическим обновлением токена
    async fetchWithAuth(url, options = {}) {
        let accessToken = this.getAccessToken();
        
        // Добавляем заголовок авторизации
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        }
        
        let response = await fetch(url, {
            ...options,
            headers,
            credentials: 'include' // Для отправки cookies
        });
        
        // Если 401 - пробуем обновить токен
        if (response.status === 401) {
            try {
                const newToken = await this.refreshToken();
                if (newToken) {
                    // Повторяем запрос с новым токеном
                    headers['Authorization'] = `Bearer ${newToken}`;
                    response = await fetch(url, {
                        ...options,
                        headers,
                        credentials: 'include'
                    });
                }
            } catch (error) {
                // Не удалось обновить токен - перенаправляем на логин
                console.error('Auth error:', error);
                await this.logout();
                throw new Error('Session expired');
            }
        }
        
        return response;
    }
}

// Создаем глобальный экземпляр
const auth = new AuthService();