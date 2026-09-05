# Stellaris Ironman Helper

Qt-програма: список сейвів Stellaris, увімкнення/вимкнення Ironman і напівпрозорий віджет чит-кодів поверх усіх вікон.

**Увімкнути Ironman** також скидає `cheated_on_save` і відновлює блок `achievement`, щоб після консолі Steam знову міг видавати досягнення. Перед правкою Stellaris має бути закрита.

```bash
python3 -m pip install -r requirements.txt
python3 stellaris_ironman.py
```

Run-скрипти Stellaris 4.x лежать у `run_scripts/`. Віджет копіює їх у
`Documents/Paradox Interactive/Stellaris/` (меню **Run → Встановити файли у Stellaris**).
У консолі гри: `run filename.txt`. Деталі — `run_scripts/README.txt`.

