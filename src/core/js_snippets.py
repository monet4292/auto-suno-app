"""JavaScript snippets used by Selenium automation.

Expose small JS scripts as Python string constants so tests and automation
can execute them via `driver.execute_script(...)`.
"""

# Script to set the value of a React-controlled <input> or <textarea> using
# the native property setter so React's internal change handlers pick up the
# change. Expects two arguments when executed via Selenium:
#   arguments[0] -> element
#   arguments[1] -> value (string)
SET_REACT_VALUE_SCRIPT = """
const el = arguments[0];
const value = arguments[1];
const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set ||
					  Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
if (nativeSetter) {
	nativeSetter.call(el, value);
} else {
	el.value = value;
}
el.dispatchEvent(new Event('input', { bubbles: true }));
el.dispatchEvent(new Event('change', { bubbles: true }));
"""
