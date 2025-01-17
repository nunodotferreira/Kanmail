import React from 'react';
import ReactDOM from 'react-dom';

import 'fonts/fontawesome/css/font-awesome.css';
import 'fonts/open-sans/css/open-sans.css';
import 'style.less';

import { setupThemes } from 'theme.js';

import ErrorBoundary from 'components/ErrorBoundary.jsx';

import settingsStore from 'stores/settings.js';

// ScrollIntoViewOptions support for Cocoa/WebKit
// Deep import for Edge: https://github.com/magic-akari/seamless-scroll-polyfill/issues/89
import { elementScrollIntoViewPolyfill } from 'seamless-scroll-polyfill/dist/es5/seamless.js';
elementScrollIntoViewPolyfill();


const bootApp = (Component, selector, getPropsFromElement=() => {}) => {
    const rootElement = document.querySelector(selector);
    if (!rootElement) {
        return;
    }

    document.body.removeChild(document.getElementById('no-app'));

    const classNames = [window.KANMAIL_PLATFORM];
    if (window.KANMAIL_FRAMELESS) {
        classNames.push('frameless');
    }

    // Load the settings *then* bootstrap the app into the DOM
    settingsStore.getSettings().then(({styleSettings}) => {
        setupThemes(styleSettings);

        const rootProps = getPropsFromElement(rootElement);
        console.debug('Settings loaded, bootstrapping app to DOM...');

        ReactDOM.render(<ErrorBoundary>
            <section className={classNames.join(' ')}>
                <Component {...rootProps} />
            </section>
        </ErrorBoundary>, rootElement);
    });
}
export default bootApp;
