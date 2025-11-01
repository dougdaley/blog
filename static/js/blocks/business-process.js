/**
 * Business Process Block for EditorJS
 * Custom block for documenting business processes with structured data
 */

class BusinessProcessBlock {
    static get toolbox() {
        return {
            title: 'Business Process',
            icon: '<svg width="14" height="14" viewBox="0 0 14 14"><path d="M2 2h10v2H2V2zm0 3h10v2H2V5zm0 3h10v2H2V8zm0 3h10v2H2v-2z"/></svg>'
        };
    }
    
    static get isReadOnlySupported() {
        return true;
    }
    
    constructor({ data, config, api, readOnly }) {
        this.data = {
            name: data.name || '',
            description: data.description || '',
            owner: data.owner || '',
            department: data.department || '',
            frequency: data.frequency || '',
            estimatedTime: data.estimatedTime || '',
            steps: data.steps || []
        };
        
        this.config = config;
        this.api = api;
        this.readOnly = readOnly;
        
        this.wrapper = undefined;
    }
    
    render() {
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'business-process-block business-block';
        
        if (this.readOnly) {
            this.wrapper.innerHTML = this.renderReadOnly();
            return this.wrapper;
        }
        
        this.wrapper.innerHTML = `
            <div class="business-process-header">
                <h4>📋 Business Process</h4>
            </div>
            
            <div class="business-process-form">
                <div class="form-row">
                    <div class="form-group">
                        <label>Process Name</label>
                        <input type="text" 
                               class="process-name" 
                               placeholder="Enter process name"
                               value="${this.data.name}">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group full-width">
                        <label>Description</label>
                        <textarea class="process-description" 
                                  placeholder="Describe the purpose and scope of this process"
                                  rows="3">${this.data.description}</textarea>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Process Owner</label>
                        <input type="text" 
                               class="process-owner" 
                               placeholder="Who owns this process?"
                               value="${this.data.owner}">
                    </div>
                    <div class="form-group">
                        <label>Department</label>
                        <input type="text" 
                               class="process-department" 
                               placeholder="Which department?"
                               value="${this.data.department}">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Frequency</label>
                        <select class="process-frequency">
                            <option value="">Select frequency</option>
                            <option value="daily" ${this.data.frequency === 'daily' ? 'selected' : ''}>Daily</option>
                            <option value="weekly" ${this.data.frequency === 'weekly' ? 'selected' : ''}>Weekly</option>
                            <option value="monthly" ${this.data.frequency === 'monthly' ? 'selected' : ''}>Monthly</option>
                            <option value="quarterly" ${this.data.frequency === 'quarterly' ? 'selected' : ''}>Quarterly</option>
                            <option value="annually" ${this.data.frequency === 'annually' ? 'selected' : ''}>Annually</option>
                            <option value="as-needed" ${this.data.frequency === 'as-needed' ? 'selected' : ''}>As Needed</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Estimated Time</label>
                        <input type="text" 
                               class="process-time" 
                               placeholder="e.g., 2-4 hours, 30 minutes"
                               value="${this.data.estimatedTime}">
                    </div>
                </div>
                
                <div class="form-group full-width">
                    <label>Process Steps</label>
                    <div class="process-steps">
                        ${this.renderSteps()}
                    </div>
                    <button type="button" class="add-step-btn">+ Add Step</button>
                </div>
            </div>
        `;
        
        this.attachEventListeners();
        return this.wrapper;
    }
    
    renderSteps() {
        if (!this.data.steps.length) {
            return '<div class="no-steps">No steps defined yet</div>';
        }
        
        return this.data.steps.map((step, index) => `
            <div class="step-item" data-step="${index}">
                <div class="step-number">${index + 1}</div>
                <div class="step-content">
                    <input type="text" 
                           class="step-title" 
                           placeholder="Step title"
                           value="${step.title || ''}">
                    <textarea class="step-description" 
                              placeholder="Describe what happens in this step"
                              rows="2">${step.description || ''}</textarea>
                    <input type="text" 
                           class="step-responsible" 
                           placeholder="Who is responsible?"
                           value="${step.responsible || ''}">
                </div>
                <button type="button" class="remove-step-btn" data-step="${index}">×</button>
            </div>
        `).join('');
    }
    
    renderReadOnly() {
        const stepsHtml = this.data.steps.map((step, index) => `
            <div class="readonly-step">
                <div class="step-number">${index + 1}</div>
                <div class="step-content">
                    <strong>${step.title || 'Untitled Step'}</strong>
                    ${step.description ? `<p>${step.description}</p>` : ''}
                    ${step.responsible ? `<small>Responsible: ${step.responsible}</small>` : ''}
                </div>
            </div>
        `).join('');
        
        return `
            <div class="readonly-business-process">
                <h4>📋 ${this.data.name || 'Untitled Process'}</h4>
                ${this.data.description ? `<p class="process-description">${this.data.description}</p>` : ''}
                
                <div class="process-meta">
                    ${this.data.owner ? `<span><strong>Owner:</strong> ${this.data.owner}</span>` : ''}
                    ${this.data.department ? `<span><strong>Department:</strong> ${this.data.department}</span>` : ''}
                    ${this.data.frequency ? `<span><strong>Frequency:</strong> ${this.data.frequency}</span>` : ''}
                    ${this.data.estimatedTime ? `<span><strong>Time:</strong> ${this.data.estimatedTime}</span>` : ''}
                </div>
                
                ${this.data.steps.length ? `
                    <div class="process-steps-readonly">
                        <h5>Process Steps:</h5>
                        ${stepsHtml}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    attachEventListeners() {
        if (this.readOnly) return;
        
        const inputs = this.wrapper.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.updateData());
            input.addEventListener('blur', () => this.updateData());
        });
        
        // Add step button
        const addBtn = this.wrapper.querySelector('.add-step-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addStep());
        }
        
        // Remove step buttons
        this.wrapper.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-step-btn')) {
                const stepIndex = parseInt(e.target.dataset.step);
                this.removeStep(stepIndex);
            }
        });
    }
    
    updateData() {
        const nameInput = this.wrapper.querySelector('.process-name');
        const descInput = this.wrapper.querySelector('.process-description');
        const ownerInput = this.wrapper.querySelector('.process-owner');
        const deptInput = this.wrapper.querySelector('.process-department');
        const freqSelect = this.wrapper.querySelector('.process-frequency');
        const timeInput = this.wrapper.querySelector('.process-time');
        
        this.data.name = nameInput ? nameInput.value : '';
        this.data.description = descInput ? descInput.value : '';
        this.data.owner = ownerInput ? ownerInput.value : '';
        this.data.department = deptInput ? deptInput.value : '';
        this.data.frequency = freqSelect ? freqSelect.value : '';
        this.data.estimatedTime = timeInput ? timeInput.value : '';
        
        // Update steps
        const stepItems = this.wrapper.querySelectorAll('.step-item');
        this.data.steps = Array.from(stepItems).map(item => {
            const titleInput = item.querySelector('.step-title');
            const descInput = item.querySelector('.step-description');
            const responsibleInput = item.querySelector('.step-responsible');
            
            return {
                title: titleInput ? titleInput.value : '',
                description: descInput ? descInput.value : '',
                responsible: responsibleInput ? responsibleInput.value : ''
            };
        });
    }
    
    addStep() {
        this.data.steps.push({
            title: '',
            description: '',
            responsible: ''
        });
        
        this.rerenderSteps();
    }
    
    removeStep(index) {
        this.data.steps.splice(index, 1);
        this.rerenderSteps();
    }
    
    rerenderSteps() {
        const stepsContainer = this.wrapper.querySelector('.process-steps');
        if (stepsContainer) {
            stepsContainer.innerHTML = this.renderSteps();
            this.attachEventListeners();
        }
    }
    
    save(blockContent) {
        this.updateData();
        return this.data;
    }
    
    validate(savedData) {
        if (!savedData.name || !savedData.name.trim()) {
            return false;
        }
        return true;
    }
}

export default BusinessProcessBlock;