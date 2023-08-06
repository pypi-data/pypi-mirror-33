# GSenha Client Python

Client for [gsenha-api](https://github.com/globocom/gsenha-api)

## Install

    pip install gsenha

## Usage

    from gsenha import PasswordManager
    pm = PasswordManager(GSENHA_ENDPOINT, GSENHA_USER, GSENHA_PASS, GSENHA_KEY|GSENHA_KEY_PATH)
    pm.get_passwords(folder, name1, name2, name*)

* GSENHA_ENDPOINT: Endpoint for [gsenha-api](https://github.com/globocom/gsenha-api)
* GSENHA_USER: User for [gsenha-api](https://github.com/globocom/gsenha-api)
* GSENHA_PASS: Password for [gsenha-api](https://github.com/globocom/gsenha-api)
* GSENHA_KEY: User's private key for [gsenha-api](https://github.com/globocom/gsenha-api)
* GSENHA\_KEY\_PATH: User's private key path for [gsenha-api](https://github.com/globocom/gsenha-api)

GSenha should use raw private key as string or load file from filesystem.

You can use these *enviroment variables* and don't pass all of them when initialize **PasswordManager**:

    from gsenha import PasswordManager
    pm = PasswordManager()
    pm.get_passwords(folder, name1, name2, name*)
    