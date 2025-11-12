<template>
  <div class="markdown-body markdown-viewer" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import javascript from 'highlight.js/lib/languages/javascript'
import 'highlight.js/styles/github-dark.css'

// 注册语言
hljs.registerLanguage('python', python)
hljs.registerLanguage('javascript', javascript)

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>'
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
  }
})

const renderedContent = computed(() => {
  return md.render(props.content || '')
})
</script>

<style>
.markdown-body.markdown-viewer {
  line-height: 1.8;
  color: #333;
}

.markdown-body.markdown-viewer h1,
.markdown-body.markdown-viewer h2,
.markdown-body.markdown-viewer h3,
.markdown-body.markdown-viewer h4 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body.markdown-viewer h1 {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body.markdown-viewer h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body.markdown-viewer h3 {
  font-size: 1.25em;
}

.markdown-body.markdown-viewer p {
  margin-bottom: 16px;
}

.markdown-body.markdown-viewer code {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  border-radius: 3px;
}

.markdown-body.markdown-viewer pre {
  background-color: #f6f8fa;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  border-radius: 6px;
  margin-bottom: 16px;
}

.markdown-body.markdown-viewer pre code {
  background-color: transparent;
  padding: 0;
}

.markdown-body.markdown-viewer ul,
.markdown-body.markdown-viewer ol {
  margin-bottom: 16px;
  padding-left: 2em;
}

.markdown-body.markdown-viewer li {
  margin-bottom: 0.25em;
}

.markdown-body.markdown-viewer blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin-bottom: 16px;
}

.markdown-body.markdown-viewer table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.markdown-body.markdown-viewer table th,
.markdown-body.markdown-viewer table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body.markdown-viewer table tr:nth-child(2n) {
  background-color: #f6f8fa;
}
</style>
