/**
 * EditorJS Configuration and Initialization
 * Sets up EditorJS with custom business blocks and sophisticated styling
 */

import EditorJS from '@editorjs/editorjs';
import Header from '@editorjs/header';
import List from '@editorjs/list';
import Quote from '@editorjs/quote';
import Delimiter from '@editorjs/delimiter';
import Table from '@editorjs/table';
import Code from '@editorjs/code';
import Raw from '@editorjs/raw';
import Embed from '@editorjs/embed';
import Image from '@editorjs/image';
import LinkTool from '@editorjs/link';

// Custom business blocks
import BusinessProcessBlock from './blocks/business-process.js';
import ControlMatrixBlock from './blocks/control-matrix.js';
import RoleDefinitionBlock from './blocks/role-definition.js';
import MaturityModelBlock from './blocks/maturity-model.js';
import ProcessFlowBlock from './blocks/process-flow.js';

class ContentEditor {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = options;
        this.editor = null;
        this.autosaveInterval = null;
        
        this.init();
    }
    
    init() {
        const defaultConfig = {
            holder: this.containerId,
            autofocus: true,
            placeholder: 'Start writing your content...',
            
            tools: {
                // Standard blocks
                header: {
                    class: Header,
                    config: {
                        placeholder: 'Enter a header',
                        levels: [1, 2, 3, 4, 5, 6],
                        defaultLevel: 2
                    }
                },
                
                list: {
                    class: List,
                    inlineToolbar: ['link', 'bold']
                },
                
                quote: {
                    class: Quote,
                    inlineToolbar: ['italic'],
                    config: {
                        quotePlaceholder: 'Enter a quote',
                        captionPlaceholder: 'Quote source'
                    }
                },
                
                delimiter: Delimiter,
                
                table: {
                    class: Table,
                    inlineToolbar: ['link', 'bold']
                },
                
                code: {
                    class: Code,
                    config: {
                        placeholder: 'Enter code...'
                    }
                },
                
                raw: {
                    class: Raw,
                    config: {
                        placeholder: 'Enter HTML code'
                    }
                },
                
                embed: {
                    class: Embed,
                    config: {
                        services: {
                            youtube: true,
                            vimeo: true,
                            coub: true
                        }
                    }
                },
                
                image: {
                    class: Image,
                    config: {
                        endpoints: {
                            byFile: '/api/upload/image',
                            byUrl: '/api/upload/image-url'
                        },
                        additionalRequestHeaders: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    }
                },
                
                linkTool: {
                    class: LinkTool,
                    config: {
                        endpoint: '/api/fetch-url'
                    }
                },
                
                // Custom business blocks
                businessProcess: {
                    class: BusinessProcessBlock,
                    config: {
                        placeholder: 'Describe the business process...'
                    }
                },
                
                controlMatrix: {
                    class: ControlMatrixBlock,
                    config: {
                        placeholder: 'Add controls to the matrix...'
                    }
                },
                
                roleDefinition: {
                    class: RoleDefinitionBlock,
                    config: {
                        placeholder: 'Define the role...'
                    }
                },
                
                maturityModel: {
                    class: MaturityModelBlock,
                    config: {
                        placeholder: 'Define maturity levels...'
                    }
                },
                
                processFlow: {
                    class: ProcessFlowBlock,
                    config: {
                        placeholder: 'Add process steps...'
                    }
                }
            },
            
            // Inline toolbar configuration
            inlineToolbar: ['link', 'marker', 'bold', 'italic'],
            
            // Events
            onChange: (api, event) => {
                this.handleChange(api, event);
            },
            
            onReady: () => {
                this.handleReady();
            }
        };
        
        // Merge with custom options
        const config = { ...defaultConfig, ...this.options };
        
        this.editor = new EditorJS(config);
    }
    
    handleReady() {
        console.log('EditorJS is ready');
        
        // Setup autosave if enabled
        if (this.options.autosave) {
            this.setupAutosave();
        }
        
        // Custom styling for sophisticated look
        this.applyStyling();
    }
    
    handleChange(api, event) {
        console.log('EditorJS content changed', event);
        
        // Emit custom event for other components to listen to
        const customEvent = new CustomEvent('editorChanged', {
            detail: { api, event }
        });
        document.dispatchEvent(customEvent);
    }
    
    applyStyling() {
        const editorElement = document.getElementById(this.containerId);
        if (!editorElement) return;
        
        // Add sophisticated styling classes
        editorElement.classList.add('editor-sophisticated');
        
        // Custom CSS for literary aesthetic
        const style = document.createElement('style');
        style.textContent = `
            .editor-sophisticated {
                font-family: "Charter", "Georgia", "Times New Roman", serif;
                line-height: 1.7;
                color: #1a1a1a;
            }
            
            .editor-sophisticated .ce-block {
                margin-bottom: 1.5rem;
            }
            
            .editor-sophisticated .ce-paragraph {
                font-size: 1.125rem;
                line-height: 1.75;
                color: #374151;
            }
            
            .editor-sophisticated .ce-header {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                font-weight: 600;
                letter-spacing: -0.01em;
                color: #111827;
            }
            
            .editor-sophisticated .ce-quote {
                border-left: 4px solid #d1d5db;
                padding-left: 2rem;
                font-style: italic;
                color: #6b7280;
            }
            
            .editor-sophisticated .ce-toolbar__content {
                max-width: 900px;
            }
            
            .editor-sophisticated .codex-editor__redactor {
                padding-bottom: 200px;
            }
            
            /* Custom business block styling */
            .business-block {
                border-left: 4px solid #3b82f6;
                background: #f0f9ff;
                padding: 1.5rem;
                margin: 2rem 0;
                border-radius: 0 0.5rem 0.5rem 0;
            }
            
            .business-block h4 {
                color: #1e3a8a;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            
            .control-block {
                border-left: 4px solid #dc2626;
                background: #fef2f2;
                padding: 1.5rem;
                margin: 2rem 0;
                border-radius: 0 0.5rem 0.5rem 0;
            }
            
            .role-block {
                border-left: 4px solid #059669;
                background: #f0fdf4;
                padding: 1.5rem;
                margin: 2rem 0;
                border-radius: 0 0.5rem 0.5rem 0;
            }
            
            .maturity-block {
                border-left: 4px solid #7c3aed;
                background: #f5f3ff;
                padding: 1.5rem;
                margin: 2rem 0;
                border-radius: 0 0.5rem 0.5rem 0;
            }
            
            .process-flow-block {
                border: 1px solid #e5e7eb;
                background: #ffffff;
                padding: 1.5rem;
                margin: 2rem 0;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
        `;
        
        document.head.appendChild(style);
    }
    
    setupAutosave() {
        if (this.autosaveInterval) {
            clearInterval(this.autosaveInterval);
        }
        
        this.autosaveInterval = setInterval(() => {
            this.save(false); // Auto-save without user notification
        }, this.options.autosaveInterval || 30000); // Default 30 seconds
    }
    
    async save(showNotification = true) {
        try {
            const outputData = await this.editor.save();
            
            // Send to server
            const response = await fetch(this.options.saveEndpoint || '/api/content/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    content: outputData,
                    id: this.options.contentId
                })
            });
            
            if (response.ok) {
                if (showNotification) {
                    this.showNotification('Content saved successfully', 'success');
                }
                
                // Emit save event
                const customEvent = new CustomEvent('editorSaved', {
                    detail: { data: outputData }
                });
                document.dispatchEvent(customEvent);
                
                return outputData;
            } else {
                throw new Error('Failed to save content');
            }
            
        } catch (error) {
            console.error('Save error:', error);
            
            if (showNotification) {
                this.showNotification('Failed to save content', 'error');
            }
            
            throw error;
        }
    }
    
    async load(data) {
        try {
            await this.editor.isReady;
            await this.editor.render(data);
            
            console.log('Content loaded successfully');
        } catch (error) {
            console.error('Load error:', error);
            throw error;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create a simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Styling
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        // Color based on type
        const colors = {
            success: '#059669',
            error: '#dc2626',
            warning: '#d97706',
            info: '#2563eb'
        };
        
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto-remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    destroy() {
        if (this.autosaveInterval) {
            clearInterval(this.autosaveInterval);
        }
        
        if (this.editor) {
            this.editor.destroy();
        }
    }
}

// Export for use in other modules
window.ContentEditor = ContentEditor;
export default ContentEditor;