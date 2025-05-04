# LL(1) Parser Analyzer

**Un proyecto educativo para construir y visualizar un analizador sintáctico LL(1) con dos interfaces:**

* **Interfaz de Escritorio** (Tkinter GUI)
* **Interfaz Web** (Streamlit + ngrok)

---

## 📖 Descripción

Este proyecto implementa un parser LL(1) completo en Python que permite:

1. **Definir gramáticas** desde un archivo `grammar.txt`.
2. **Calcular conjuntos FIRST y FOLLOW** automáticamente.
3. **Construir la tabla de análisis LL(1)** y la tabla de recuperación de errores (modo pánico).
4. **Analizar cadenas de entrada**, mostrando paso a paso la pila, el token actual y la regla aplicada.
5. **Visualizar**:

   * La tabla de parseo y recuperación de errores.
   * El árbol de derivación de una cadena válida.

Todo ello accesible desde:

* 🖥️ **Escritorio** con Tkinter (`ll_parser_gui.py`).
* 🌐 **Web** con Streamlit (`app.py`), que puede exponerse públicamente usando ngrok.

---

## ⚙️ Requisitos

* **Python** 3.8 o superior
* **Graphviz** (para el layout de árboles)
* Bibliotecas Python (definidas en `requirements.txt`):

```bash
pip install -r requirements.txt
```

pip install streamlit pandas matplotlib networkx pydot pygraphviz

````
También se usan paquetes de la librería estándar: `re`, `json`, `tkinter`.

> **Nota**: En distribuciones Linux, instalar `graphviz` y `python3-tk`:
> ```bash
> sudo apt update
> sudo apt install graphviz python3-tk
> ```

---

## 📂 Estructura de archivos

```text
├── LL_parser.py           # Núcleo del parser LL(1)
├── ll_parser_gui.py       # GUI de escritorio (Tkinter)
├── app.py                 # Interfaz web con Streamlit
├── grammar.txt            # Gramática de ejemplo (input)
├── requirements.txt       # dependencias pip
└── README.md              # Este documento
````

---

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-proyecto>
cd LL1-Parser-Analyzer
```

### 2. Crear entorno virtual (opcional)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ejecutar Interfaz de Escritorio

```bash
python ll_parser_gui.py
```

* Carga o edita tu `grammar.txt`.
* Valida si la gramática es LL(1).
* Ingresa cadenas de prueba y observa el análisis paso a paso.
* Visualiza tablas y árbol de derivación.

### 4. Ejecutar Interfaz Web (Streamlit)

```bash
streamlit run app.py
```

* Abre en el navegador `http://localhost:8501` (o el puerto que indique).
* Alterna entre mostrar la Tabla LL(1) y la Tabla de Recuperación.
* Analiza cadenas desde la barra lateral.

#### 4.1. Exponer con ngrok

Para que cualquier persona acceda a tu app web:

1. Instala y configura tu authtoken de ngrok:

   ```bash
   ngrok config add-authtoken <tu-authtoken>
   ```
2. Lanza el túnel hacia tu servidor local:

   ```bash
   ngrok http 8501
   ```
3. Comparte la URL pública que ngrok te muestre.

---

## ✍️ Ejemplos de Gramáticas

### 1. Expresiones Aritméticas

```bnf
E → E + T | E - T | T
T → T * F | T / F | F
F → ( E ) | id
```

### 2. Gramática con epsilon

```bnf
S → A B
A → a A | ε
B → b B | c
```

### 3. Gramática simple de asignaciones

```bnf
S → id = E ;
E → E + T | T
T → T * F | F
F → ( E ) | id | num
```

Guarda cualquiera en `grammar.txt` usando `->` o `→` y barras `|` para alternativas.

---

## 📚 Conceptos Clave

### FIRST(X)

Conjunto de símbolos terminales que pueden aparecer al comienzo de alguna cadena derivada desde X.

* **Reglas**:

  1. Si X es terminal, FIRST(X) = {X}.
  2. Si X → ε, ε ∈ FIRST(X).
  3. Si X → Y₁ Y₂ … Yₙ, entonces:

     * Incluye FIRST(Y₁) \ {ε}.
     * Si ε ∈ FIRST(Y₁), incluye FIRST(Y₂), y así sucesivamente.

### FOLLOW(A)

Conjunto de terminales que pueden seguir inmediatamente a A en alguna derivación.

* **Reglas**:

  1. `$` ∈ FOLLOW(S) si S es símbolo inicial.
  2. Si A → α B β, todo terminal en FIRST(β) \ {ε} ∈ FOLLOW(B).
  3. Si A → α B β y ε ∈ FIRST(β), o A → α B, entonces FOLLOW(A) ⊆ FOLLOW(B).

### Tabla de Análisis LL(1)

Filas: No terminales. Columnas: terminales + `$`.

* Para cada producción A → α:

  * Por cada `a ∈ FIRST(α) \ {ε}`, tabla\[A,a] = A→α.
  * Si ε ∈ FIRST(α), tabla\[A,b] = A→α para todo b ∈ FOLLOW(A).

### Recuperación de Errores (Panic Mode)

* **EXT**: si el token actual está en FOLLOW(A), hacer *pop* de A.
* **EP**: si no está en FIRST(A) ni en FOLLOW(A), descartar el token de entrada.
* **–**: caso sin acción (entrada esperada).

### Árbol de Derivación

Representación gráfica de cómo la gramática genera la cadena de entrada:

* Cada nodo es un símbolo;
* Las ramas siguen las producciones aplicadas.

---

---

## 📸 Capturas de Pantalla

### Interfaz de Escritorio (Tkinter GUI)

<!-- Reemplaza `path/to/gui_screenshot.png` con la ruta real de tu imagen -->
1.- Colocamos una gramática en el grammar input, para luego guardarla con el boton save grammar, podemos observar las tablas de FIRST y FOLLOW al momento de aplastar el boton de Load Grammar
![image](https://github.com/user-attachments/assets/2939cfab-c3cc-4fbc-bdda-2b3277f6419e)
2.- Podemos tambien analizar el input string  colocando la cadena donde se verificara que si es valido o no. Algo interesante de esta interfaz es el boton step quien te enseñara en tiempo real como se va creando los match hasta terminar de recorrer la cadena buscando su regla. 
![image](https://github.com/user-attachments/assets/f9d4de21-f8f2-47fc-9118-db42a061a120)
3.- Tambien podemos observar la tabla de parser 
![image](https://github.com/user-attachments/assets/6d5a735f-4eb7-46ff-84b0-64de86b1f0f6)
4.- La tabla de recuperacion de errores, donde se muestra los Extrar y Explorar
![image](https://github.com/user-attachments/assets/dd5d5ee2-196b-4c8d-839d-2a1fa9f0d58d)
5.- Y por ultimo se muestra un arbol de derivacion 
![image](https://github.com/user-attachments/assets/15f6fe07-9aed-4e88-8b85-f5d55d7f51a0)

### Interfaz Web (Streamlit + ngrok)
0.- al ingresar veremos asi la pagina
![image](https://github.com/user-attachments/assets/2cfa955e-fa74-4704-9621-acd6687e4f8f)
1.- Reload grammar para guardar la gramática
![image](https://github.com/user-attachments/assets/9eee8a94-128a-4bde-ba4a-627f5280a1b5)
2.- Se puede acceder a las dos tablas respectivamente (parser y recueperación de errores)
![image](https://github.com/user-attachments/assets/345bbd4e-c793-46e8-ae1b-565a20347814)
3.- Finalmente podemos analizar la cadena
![image](https://github.com/user-attachments/assets/189458f7-8427-4626-88e0-96278ad89152)


<!-- Reemplaza `path/to/ngrok_screenshot.png` con la ruta real de tu imagen -->

![Streamlit con ngrok](path/to/ngrok_screenshot.png)

**URL pública (ejemplo):** [https://0ac8-181-176-90-151.ngrok-free.app/](https://0ac8-181-176-90-151.ngrok-free.app/)

<!-- Reemplaza `path/to/ngrok_screenshot.png` con la ruta real de tu imagen -->

![Streamlit con ngrok](path/to/ngrok_screenshot.png)
