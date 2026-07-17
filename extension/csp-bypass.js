// CSP Bypass — Content Script
// 在 document_start 阶段通知 service worker 通过 CDP 绕过 CSP
chrome.runtime.sendMessage({ action: 'bypassCSP' });
