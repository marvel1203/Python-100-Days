import request from '@/utils/request'

export const courseApi = {
  // 获取课程分类
  getCategories() {
    return request.get('/courses/categories/')
  },
  
  // 获取课程列表
  getCourses(params) {
    return request.get('/courses/courses/', { params })
  },
  
  // 获取课程详情
  getCourseDetail(slug) {
    return request.get(`/courses/courses/${slug}/`)
  },
  
  // 点赞课程
  likeCourse(slug) {
    return request.post(`/courses/courses/${slug}/like/`)
  },
  
  // 获取课时列表
  getLessons(params) {
    return request.get('/courses/lessons/', { params })
  },
  
  // 获取课时详情
  getLessonDetail(slug) {
    return request.get(`/courses/lessons/${slug}/`)
  },
  
  // 点赞课时
  likeLesson(slug) {
    return request.post(`/courses/lessons/${slug}/like/`)
  },
}

export const progressApi = {
  // 获取学习进度
  getProgress(params) {
    return request.get('/courses/progress/', { params })
  },
  
  // 更新学习进度
  updateProgress(id, data) {
    return request.patch(`/courses/progress/${id}/`, data)
  },
  
  // 创建学习进度
  createProgress(data) {
    return request.post('/courses/progress/', data)
  },
  
  // 获取学习统计
  getStatistics() {
    return request.get('/courses/progress/statistics/')
  },
}

export const noteApi = {
  // 获取笔记列表
  getNotes(params) {
    return request.get('/courses/notes/', { params })
  },
  
  // 创建笔记
  createNote(data) {
    return request.post('/courses/notes/', data)
  },
  
  // 更新笔记
  updateNote(id, data) {
    return request.patch(`/courses/notes/${id}/`, data)
  },
  
  // 删除笔记
  deleteNote(id) {
    return request.delete(`/courses/notes/${id}/`)
  },
  
  // 点赞笔记
  likeNote(id) {
    return request.post(`/courses/notes/${id}/like/`)
  },
}

export const exerciseApi = {
  // 获取练习列表
  getExercises(params) {
    return request.get('/exercises/exercises/', { params })
  },
  
  // 获取练习详情
  getExerciseDetail(slug) {
    return request.get(`/exercises/exercises/${slug}/`)
  },
  
  // 运行代码
  runCode(data) {
    return request.post('/exercises/exercises/run_code/', data)
  },
  
  // 提交代码
  submitCode(exerciseSlug, data) {
    return request.post('/exercises/submissions/', {
      ...data,
      exercise: exerciseSlug
    })
  },
  
  // 获取提交记录
  getSubmissions(params) {
    return request.get('/exercises/submissions/', { params })
  },
  
  // 获取提交统计
  getSubmissionStatistics() {
    return request.get('/exercises/submissions/statistics/')
  },
}
