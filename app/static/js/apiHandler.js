const API = {
    async fetch(endpoint, options = {}) {
        try {
            const url = endpoint.includes('?') 
                ? `${endpoint}&format=json`
                : `${endpoint}?format=json`;
                
            const response = await fetch(url, {
                headers: {
                    'Accept': 'application/json'
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Something went wrong');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    getSubjects() {
        return this.fetch('/user/subjects');
    },
    
    getSubject(subjectId) {
        return this.fetch(`/user/subjects/${subjectId}`);
    },
    
    getChaptersBySubject(subjectId) {
        return this.fetch(`/user/subjects/${subjectId}/chapters`);
    },
    
    getChapter(chapterId) {
        return this.fetch(`/user/chapters/${chapterId}`);
    },
    
    getQuizzesByChapter(chapterId) {
        return this.fetch(`/user/chapters/${chapterId}/quizzes`);
    },
    
    getQuiz(quizId) {
        return this.fetch(`/user/quizzes/${quizId}`);
    },
    
    getQuizQuestions(quizId) {
        return this.fetch(`/user/quizzes/${quizId}/questions`);
    },
    
    submitQuiz(quizId, answers) {
        return this.fetch(`/user/quizzes/${quizId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers })
        });
    },
    
    getUserScores() {
        return this.fetch(`/user/scores`);
    },
    
    search(query, type = 'all') {
        return this.fetch(`/user/search?query=${encodeURIComponent(query)}&type=${type}`);
    },
    
    getDashboard() {
        return this.fetch('/user/dashboard');
    },
    
    admin: {
        getDashboard() {
            return API.fetch('/admin/dashboard');
        },
        
        getSubjects() {
            return API.fetch('/admin/subjects');
        },
        
        getSubject(subjectId) {
            return API.fetch(`/admin/subjects/${subjectId}`);
        },
        
        getChapters() {
            return API.fetch('/admin/chapters');
        },
        
        getChapter(chapterId) {
            return API.fetch(`/admin/chapters/${chapterId}`);
        },
        
        getQuizzes() {
            return API.fetch('/admin/quizzes');
        },
        
        getQuiz(quizId) {
            return API.fetch(`/admin/quizzes/${quizId}`);
        },
        
        getQuizQuestions(quizId) {
            return API.fetch(`/admin/quizzes/${quizId}/questions`);
        },
        
        getUsers() {
            return API.fetch('/admin/users');
        },
        
        search(query, type = 'all') {
            return API.fetch(`/admin/search?query=${encodeURIComponent(query)}&type=${type}`);
        }
    }
}; 