/* Compatibility shim for vendored React 16.0: JSX <> fragments return child arrays. */
'use strict';
if (!window.React.Fragment) {
  window.React.Fragment = function Fragment(props) { return window.React.Children.toArray(props.children); };
}
