# gswiki
MoinMoin wiki plugin for GS3

*Since GS3 is Japan-local game, I'm not considering for i18n this project. All UI strings are hard-coded in the source file.*

# INSTALL
1. Download MoinMoin 1.x from MoinMoin official website. Please see the MoinMoin's INSTALL document for installing MoinMoin.
2. Download this project, place it to anywhere you like.
3. Edit wikiconfig.py in MoinMoin's root directory like this:

    plugin_dir = ["*where you extracted the project in Step 2.*"]

4. Add a link to theme directories:

    cd <*MoinMoin root*>/web/static/htdocs
    
    ln -s <*where you extracted the project in Step 2.*>/gs2mobile gs2mobile
    
    ln -s <*where you extracted the project in Step 2.*>/gs3mobile gs3mobile

5. Run wikiserver.py at the MoinMoin's root directory.

Hopefully this works. This project is just a simple plugin for MoinMoin, so please see MoinMoin's document for the installation details.
