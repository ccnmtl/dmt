module.exports = {
    "env": {
        "browser": true,
        "amd": true,
        "jquery": true
    },
    "plugins": [
        "security",
        "scanjs-rules",
        "no-unsafe-innerhtml"
    ],
    "extends": [
        "eslint:recommended",
        "plugin:security/recommended"
    ],  
    "extends": "eslint:recommended",
    "rules": {
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "no-unused-vars": [
            "error",
            {"vars": "all", "args": "none"}
        ],
        "quotes": [
            "error",
            "single"
        ],
        "semi": [
            "error",
            "always"
        ],
        /** no-unsafe-innerhtml rule **/
        "no-unsafe-innerhtml/no-unsafe-innerhtml" : 2,

        /** ScanJS rules **/
        "scanjs-rules/assign_to_hostname": 1,
        "scanjs-rules/assign_to_href": 1,
        "scanjs-rules/assign_to_location": 1,
        "scanjs-rules/assign_to_onmessage": 1,
        "scanjs-rules/assign_to_pathname": 1,
        "scanjs-rules/assign_to_protocol": 1,
        "scanjs-rules/assign_to_search": 1,
        "scanjs-rules/assign_to_src": 1,
        "scanjs-rules/call_Function": 1,
        "scanjs-rules/call_addEventListener": 1,
        "scanjs-rules/call_addEventListener_deviceproximity": 1,
        "scanjs-rules/call_addEventListener_message": 1,
        "scanjs-rules/call_connect": 1,
        "scanjs-rules/call_eval": 1,
        "scanjs-rules/call_execScript": 1,
        "scanjs-rules/call_hide": 1,
        "scanjs-rules/call_open_remote=true": 1,
        "scanjs-rules/call_parseFromString": 1,
        "scanjs-rules/call_setImmediate": 1,
        "scanjs-rules/call_setInterval": 1,
        "scanjs-rules/call_setTimeout": 1,
        "scanjs-rules/identifier_indexedDB": 1,
        "scanjs-rules/identifier_localStorage": 1,
        "scanjs-rules/identifier_sessionStorage": 1,
        "scanjs-rules/new_Function": 1,
        "scanjs-rules/property_addIdleObserver": 1,
        "scanjs-rules/property_createContextualFragment": 1,
        "scanjs-rules/property_geolocation": 1,
        "scanjs-rules/property_getUserMedia": 1,
        "scanjs-rules/property_indexedDB": 1,
        "scanjs-rules/property_localStorage": 1,
        "scanjs-rules/property_mgmt": 1,
        "scanjs-rules/property_sessionStorage": 1,

        'security/detect-buffer-noassert': 'warn',
        'security/detect-child-process': 'warn',
        'security/detect-disable-mustache-escape': 'warn',
        'security/detect-eval-with-expression': 'warn',
        'security/detect-new-buffer': 'warn',
        'security/detect-no-csrf-before-method-override': 'warn',
        'security/detect-non-literal-fs-filename': 'warn',
        'security/detect-non-literal-regexp': 'warn',
        'security/detect-non-literal-require': 'warn',
        'security/detect-object-injection': 'warn',
        'security/detect-possible-timing-attacks': 'warn',
        'security/detect-pseudoRandomBytes': 'warn',
        'security/detect-unsafe-regex': 'warn'
    }
};
