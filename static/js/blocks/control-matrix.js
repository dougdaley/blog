/**
 * Control Matrix Block for EditorJS
 * Simple implementation for control documentation
 */

class ControlMatrixBlock {
    static get toolbox() {
        return {
            title: 'Control Matrix',
            icon: '🛡️'
        };
    }
    
    constructor({ data }) {
        this.data = data || { controls: [] };
    }
    
    render() {
        const wrapper = document.createElement('div');
        wrapper.className = 'control-matrix-block control-block';
        
        wrapper.innerHTML = `
            <h4>🛡️ Control Matrix</h4>
            <textarea placeholder="List controls, one per line in format: ID | Description | Type | Risk Level">${this.data.controls.join('\n')}</textarea>
        `;
        
        const textarea = wrapper.querySelector('textarea');
        textarea.addEventListener('input', () => {
            this.data.controls = textarea.value.split('\n').filter(line => line.trim());
        });
        
        return wrapper;
    }
    
    save() {
        return this.data;
    }
}

export default ControlMatrixBlock;