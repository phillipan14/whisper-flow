.PHONY: app dmg clean

app:
	./venv/bin/pyinstaller Philoquent.spec --noconfirm
	codesign --force --deep --sign - dist/Philoquent.app

dmg: app
	create-dmg \
		--volname "Philoquent" \
		--window-pos 200 120 \
		--window-size 600 400 \
		--icon-size 100 \
		--icon "Philoquent.app" 150 190 \
		--app-drop-link 450 190 \
		--hide-extension "Philoquent.app" \
		"Philoquent-0.1.0.dmg" \
		"dist/"

clean:
	rm -rf build dist *.dmg
