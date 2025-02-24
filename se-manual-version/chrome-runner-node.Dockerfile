FROM selenium/node-chrome
CMD [ "java", "-jar", "/opt/selenium/selenium-server.jar", "standalone", "--max-sessions", "1" ]
