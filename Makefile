APP_NAME = DataFlux
ENTRY = main.py

build:
	pyinstaller --onedir --name $(APP_NAME) --add-data "assets/fonts:assets/fonts" --add-data "assets/images:assets/images" $(ENTRY)

clean:
	rm -rf build dist *.spec
