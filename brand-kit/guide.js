document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
        const value = button.dataset.copy;
        const status = document.getElementById('copy-status');
        try {
            await navigator.clipboard.writeText(value);
            status.textContent = `${value} 복사했습니다.`;
        } catch {
            status.textContent = `색상 코드: ${value}`;
        }
    });
});
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
