/** @odoo-module **/
/**
 * Promotion Grid — Card click delegator
 * Toggles the checkbox when clicking anywhere on the card.
 */
document.addEventListener('click', (ev) => {
    const card = ev.target.closest('.o_promotion_card');
    if (!card) return;
    // Don't re-toggle if the user clicked exactly on the checkbox
    if (ev.target.tagName === 'INPUT') return;
    const cb = card.querySelector('input[type="checkbox"]');
    if (cb) {
        cb.checked = !cb.checked;
        cb.dispatchEvent(new Event('change', { bubbles: true }));
    }
});
