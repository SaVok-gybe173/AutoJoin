pyinstaller --name AutoJoin --clean \
    --add-data "venv/lib/python3.12/site-packages/pyfiglet/fonts:pyfiglet/fonts" \
    main.py