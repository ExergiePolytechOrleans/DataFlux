APP_NAME = DataFlux
ENTRY = main.py

build:
	uv run pyinstaller --onedir --windowed --name $(APP_NAME) --paths src --add-data "assets/fonts:assets/fonts" --add-data "assets/images:assets/images" $(ENTRY)

clean:
	rm -rf build dist *.spec
