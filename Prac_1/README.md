# Практическое занятие №1  
## Введение, основы работы в командной строке

---

## Задача 1

Вывести отсортированный в алфавитном порядке список имён пользователей в файле `/etc/passwd`.

### Решение

```bash
sort /etc/passwd | cut -d ":" -f1
```

### Объяснение

- `sort /etc/passwd` — сортирует строки файла `/etc/passwd`;
- `cut -d ":" -f1` — использует `:` как разделитель и выводит первое поле;
- первое поле в `/etc/passwd` — имя пользователя.

---

## Задача 2

Вывести данные `/etc/protocols` в отсортированном порядке для 5 наибольших номеров протоколов.

### Решение

```bash
sort -nr -k2 /etc/protocols | head -n 5 | awk '{print $2, $1}'
```

### Результат

```text
262 mptcp
143 ethernet
142 rohc
141 wesp
140 shim6
```

### Объяснение

- `sort -nr -k2` — сортирует по второму столбцу как числа, от большего к меньшему;
- `head -n 5` — оставляет первые 5 строк;
- `awk '{print $2, $1}'` — выводит сначала номер протокола, затем его имя.

---

## Задача 3

Написать программу `banner` средствами Bash для вывода текста в рамке. Размер рамки должен зависеть от длины текста.

### Решение

```bash
#!/usr/bin/env bash

text="$1"

border="+"

for ((i=0; i<${#text}+2; i++)); do
    border="${border}-"
done

border="${border}+"

echo "$border"
echo "| $text |"
echo "$border"
```

### Запуск

```bash
chmod +x banner
./banner "Hello from RTU MIREA!"
```

### Результат

```text
+-----------------------+
| Hello from RTU MIREA! |
+-----------------------+
```

### Проверка ShellCheck

```bash
shellcheck banner
```

---

## Задача 4

Написать программу для вывода всех идентификаторов в файле без повторений.

### Решение

```bash
#!/usr/bin/env bash

grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | tr '\n' ' '
echo
```

### Запуск

```bash
chmod +x identifiers
./identifiers hello.c
```

### Результат

```text
h Hello include int main n printf return stdio void World
```

### Объяснение

- `grep -oE` — находит фрагменты текста по регулярному выражению;
- `[A-Za-z_][A-Za-z0-9_]*` — шаблон идентификатора;
- `sort -u` — сортирует и удаляет повторения;
- `tr '\n' ' '` — заменяет переносы строк пробелами.

---

## Задача 5

Написать программу для регистрации пользовательской команды: установить правильные права доступа и скопировать программу в `/usr/local/bin`.

### Решение

```bash
#!/usr/bin/env bash

chmod 755 "$1"
sudo cp "$1" /usr/local/bin/
sudo chmod 755 "/usr/local/bin/$(basename "$1")"
```

### Запуск

Сделать программу `reg` исполняемой:

```bash
chmod +x reg
```

Зарегистрировать программу `banner`:

```bash
./reg banner
```

После этого команду можно запускать без `./`:

```bash
banner "Hello"
```

Проверить расположение команды:

```bash
which banner
```

Результат:

```text
/usr/local/bin/banner
```

### Объяснение

- `chmod 755 "$1"` — устанавливает права доступа к программе;
- `sudo cp "$1" /usr/local/bin/` — копирует программу в каталог `/usr/local/bin`;
- `basename "$1"` — получает имя файла без пути;
- `sudo chmod 755` — устанавливает права доступа для скопированной программы;
- после копирования в `/usr/local/bin` программу можно запускать просто по имени.

---

## Задача 6

Написать программу для проверки наличия комментария в первой строке файлов с расширениями `.c`, `.js` и `.py`.

### Решение

```bash
#!/usr/bin/env bash

for file in *.c *.js *.py; do
    [ -e "$file" ] || continue

    case "$file" in
        *.py)
            if head -n 1 "$file" | grep -qE '^[[:space:]]*#'; then
                echo "$file: комментарий есть"
            else
                echo "$file: комментария нет"
            fi
            ;;

        *.c|*.js)
            if head -n 1 "$file" | grep -qE '^[[:space:]]*(//|/\*)'; then
                echo "$file: комментарий есть"
            else
                echo "$file: комментария нет"
            fi
            ;;
    esac
done
```

### Запуск

```bash
chmod +x check_comments
./check_comments
```

### Результат

```text
hello.c: комментария нет
text.c: комментарий есть
text.js: комментарий есть
text.py: комментария нет
```

### Объяснение

- `for` перебирает файлы `.c`, `.js` и `.py`;
- `head -n 1` получает первую строку файла;
- `grep -qE` проверяет наличие комментария;
- `case` определяет расширение файла;
- `if` выводит результат проверки.

---

## Задача 7

Написать программу для нахождения файлов-дубликатов по заданному пути и его подкаталогам.

### Решение

```bash
#!/usr/bin/env bash

if [ ! -d "$1" ]; then
    echo "Каталог не найден"
    exit 1
fi

find "$1" -type f -exec sha256sum {} + |
    sort |
    uniq -w 64 -D |
    cut -c 67-
```

### Запуск

```bash
chmod +x find_duplicates
./find_duplicates duplicates
```

### Результат

```text
duplicates/file1.txt
duplicates/file2.txt
```

### Объяснение

- `find "$1" -type f` — ищет все файлы по указанному пути и в подкаталогах;
- `sha256sum` — вычисляет хеш содержимого каждого файла;
- `sort` — сортирует строки с хешами;
- `uniq -w 64 -D` — оставляет только файлы с одинаковыми хешами;
- `cut -c 67-` — убирает хеш и выводит только путь к файлу.

---

## Задача 8

Написать программу, которая находит все файлы в указанном каталоге с расширением, переданным в качестве аргумента, и архивирует их в `tar`.

### Решение

```bash
#!/usr/bin/env bash

if [ ! -d "$1" ]; then
    echo "Каталог не найден"
    exit 1
fi

find "$1" -maxdepth 1 -type f -name "*.$2" -print0 |
    tar --null -cvf archive.tar --files-from=-
```

### Запуск

```bash
chmod +x archive_files
./archive_files duplicates txt
```

### Проверка архива

```bash
tar -tf archive.tar
```

### Результат

```text
duplicates/file3.txt
duplicates/b.txt
duplicates/file2.txt
duplicates/a.txt
duplicates/file1.txt
```

### Объяснение

- `find` ищет файлы в указанном каталоге;
- `-maxdepth 1` ограничивает поиск только этим каталогом;
- `-type f` выбирает обычные файлы;
- `-name "*.$2"` ищет файлы с нужным расширением;
- `tar -cvf` создаёт архив `archive.tar`;
- `--files-from=-` получает список файлов из предыдущей команды.

---

## Задача 9

Написать программу, которая заменяет в файле последовательности из 4 пробелов на символ табуляции. Входной и выходной файлы задаются аргументами.

### Решение

```bash
#!/usr/bin/env bash

if [ ! -f "$1" ]; then
    echo "Входной файл не найден"
    exit 1
fi

if [ "$1" = "$2" ]; then
    echo "Входной и выходной файлы должны отличаться"
    exit 1
fi

sed $'s/    /\t/g' "$1" > "$2"
```

### Запуск

```bash
chmod +x spaces_to_tabs
./spaces_to_tabs input.txt output.txt
```

### Проверка

```bash
cat -T output.txt
```

### Результат

```text
one^Itwo
three^Ifour
```

### Объяснение

- `sed` выполняет замену текста;
- `s/    /\t/g` заменяет последовательности из 4 пробелов на табуляцию;
- `$1` — входной файл;
- `$2` — выходной файл;
- `>` записывает результат в выходной файл;
- `cat -T` показывает символ табуляции как `^I`.

---

## Задача 10

Написать программу, которая выводит названия всех пустых текстовых файлов в указанной директории.

### Решение

```bash
#!/usr/bin/env bash

if [ ! -d "$1" ]; then
    echo "Каталог не найден"
    exit 1
fi

find "$1" -maxdepth 1 -type f -name "*.txt" -empty -printf "%f\n"
```

### Запуск

```bash
chmod +x empty_txt
./empty_txt empty_test
```

### Результат

```text
b.txt
a.txt
```

### Объяснение

- `find` выполняет поиск файлов;
- `-maxdepth 1` ограничивает поиск указанной директорией;
- `-type f` выбирает обычные файлы;
- `-name "*.txt"` выбирает файлы с расширением `.txt`;
- `-empty` оставляет только пустые файлы;
- `-printf "%f\n"` выводит только имя файла без пути.

---

## Проверка ShellCheck

Bash-скрипты были проверены на ошибки и предупреждения с помощью ShellCheck.

```bash
shellcheck banner
shellcheck identifiers
shellcheck reg
shellcheck check_comments
shellcheck find_duplicates
shellcheck archive_files
shellcheck spaces_to_tabs
shellcheck empty_txt
```

При проверке ShellCheck предупреждений не обнаружено.
