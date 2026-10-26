# Ciclos de la economía de Río Negro — Empleo, recaudación, salarios y gasto público

Visor interactivo, autocontenido y sin dependencias de compilación. Estima la tendencia, extrae el ciclo y fecha los puntos de giro de cuatro series de la provincia de Río Negro, todas en la misma ventana temporal:

- el empleo asalariado privado registrado, que se usa como serie de referencia;
- la recaudación del Impuesto sobre los Ingresos Brutos;
- la remuneración promedio de los asalariados registrados;
- el gasto público provincial ejecutado.

Trabaja con las tres nociones de ciclo de la literatura —clásico, de crecimiento y de tasas— (Harding y Pagan, 2002; Zarnowitz y Ozyildirim, 2006). Es la versión provincial de [Ciclos de la economía argentina](https://fcontiggiani.github.io/ciclo-argentina/).

**[▶ Abrir el visor](https://fcontiggiani.github.io/ciclo-rionegro/ciclo-rionegro.html)**

![Captura del visor de ciclos de Río Negro, mostrando el panel de controles (series, ventana de datos, método de tendencia y tipo de ciclo) y los paneles del empleo privado registrado y de la recaudación de IIBB en el ciclo de crecimiento, con los picos y valles fechados y las contracciones sombreadas](screenshot-visor.png)

---

## Descripción

| Serie | Papel | Frecuencia | Unidad | Fuente |
|---|---|---|---|---|
| Asalariados registrados del sector privado, desestacionalizado | Referencia | Mensual | miles de asalariados | SIPA (OEDE), vía API Series de Tiempo |
| Recaudación del Impuesto sobre los Ingresos Brutos | Recaudación | Trimestral | millones de $ de 2025 por trimestre | DNAP, Recursos tributarios de origen provincial (información de la ARTRN) |
| Remuneración promedio de los asalariados registrados del sector privado | Salarios | Mensual | $ de 2025 por mes | SIPA (OEDE), Remuneraciones por provincia |
| Gasto total de la Administración Pública No Financiera | Gasto | Trimestral | millones de $ de 2025 por trimestre | DNAP, Ejecuciones presupuestarias provinciales |

Las cuatro series cubren la **misma ventana**: desde enero de 2011 (primer trimestre con ejecución presupuestaria trimestral publicada) hasta el último período común (actualmente junio de 2026 / 2026 T2). Las series nominales se expresan en pesos constantes con el **IPIM nacional del INDEC** y se desestacionalizan.

**Por qué el empleo y no el PIB.** No existe un PIB trimestral oficial de Río Negro. El INDEC publica el PIB por provincia solo para el año base 2004, como parte de la regionalización de las cuentas nacionales. Las estimaciones anuales disponibles (Dirección de Estadística y Censos provincial, CEPAL, DNAP) no permiten fechar ciclos. El empleo asalariado privado registrado es una serie mensual, observada y desestacionalizada por la fuente, y un indicador coincidente habitual de la actividad provincial.

El objetivo didáctico es doble. Por un lado, muestra que **los puntos de giro dependen de la definición de ciclo y del método de tendencia**. Por otro, permite contrastar el ciclo del empleo con el de las variables fiscales y salariales de la provincia: la recaudación de IIBB, ligada a la facturación; el salario real; y el gasto público, que puede amplificar o amortiguar el ciclo.

## Características principales

| Panel / control | Descripción |
|---|---|
| **Series** | Casillas para mostrar u ocultar cada serie; cada una se dibuja en su propio panel con eje vertical independiente y eje temporal compartido. |
| **Ventana de datos** | Cotas inferior y superior con resolución mensual y atajos (toda la muestra, 2011–2019, 2016–hoy, 2020–hoy). La ventana define la muestra con la que se estiman la tendencia y los giros. |
| **Tendencia** | Hodrick–Prescott (λ trimestral seleccionable, reescalado para series mensuales), filtro de Hamilton, tendencia log-lineal, log-cuadrática y media móvil centrada; casilla para mostrar u ocultar su gráfica. |
| **Tipo de ciclo** | Clásico (nivel, con escala logarítmica opcional), de crecimiento (desvío porcentual respecto de la tendencia) o de tasas (variación interanual). |
| **Puntos de giro** | Picos (▼) y valles (△) fechados con reglas de Bry–Boschan sobre la serie que se muestra; sombreado opcional de las contracciones. |
| **Resumen por serie** | Número de picos y valles, duración media de expansiones y contracciones, última fase y tabla de giros. |
| **Concordancia con el empleo** | Para cada giro del empleo, giro del mismo tipo más cercano en las otras series, con el desfase en meses (negativo = adelanto) y su mediana. |
| **Contraste entre tipos de ciclo** | Tabla por serie con las fechas de cada giro según el ciclo de tasas, de crecimiento y clásico, y el desfase respecto del ciclo de crecimiento. |
| **Tema claro / oscuro** | Conmutador persistido por navegador. |

## Fundamento teórico

### Tres nociones de ciclo

1. **Ciclo clásico** (Burns y Mitchell, 1946): expansiones y contracciones en el **nivel** de la serie.
2. **Ciclo de crecimiento**: fluctuaciones del **desvío respecto de la tendencia**, *c(t) = 100 · [ln y(t) − τ(t)]*.
3. **Ciclo de tasas**: fluctuaciones de la **variación interanual**, *g(t) = 100 · [y(t) / y(t − s) − 1]*, con *s* = 4 trimestres o 12 meses.

En torno a un pico se espera la secuencia **tasas → crecimiento → clásico**, porque la tasa aproxima la derivada del nivel y el desvío resta una tendencia suave.

### Métodos de tendencia

Todos se estiman sobre el logaritmo de la serie y **solo con los datos de la ventana elegida**:

| Método | Definición | Parámetros |
|---|---|---|
| Hodrick–Prescott (1997) | min Σ [ln y(t) − τ(t)]² + λ Σ [Δ²τ(t)]² | λ trimestral seleccionable; para series mensuales se multiplica por 3⁴ (Ravn y Uhlig, 2002) |
| Filtro de Hamilton (2018) | τ(t + h) = valor ajustado de regresar ln y(t + h) sobre 1, ln y(t), …, ln y(t − p + 1) | h = 2 años, p = 1 año |
| Log-lineal / log-cuadrática | Mínimos cuadrados de ln y(t) sobre un polinomio en *t* | Grado 1 o 2 |
| Media móvil centrada | Media de 2 × m términos | m = 2, 3 o 5 años |

### Fechado de los puntos de giro

Versión simplificada de Bry y Boschan (1971):

1. **Candidatos**: extremos locales en una ventana de ±5 meses (±2 trimestres en las series trimestrales).
2. **Alternancia**: entre dos giros consecutivos del mismo tipo se conserva el más extremo.
3. **Censura**: fase mínima de 6 meses (2 trimestres), ciclo mínimo de 15 meses (5 trimestres) y ningún giro a menos de 6 meses (2 trimestres) de los extremos de la ventana.

Para las series trimestrales se siguen las reglas de Harding y Pagan (2002).

### Concordancia y contraste

- **Concordancia con el empleo.** Para cada giro del empleo se busca el giro del mismo tipo más cercano en las otras series, entre 24 meses antes y 12 meses después, sin reutilizar giros. Se comparan los meses centrales de cada período (el segundo mes del trimestre en las series trimestrales).
- **Contraste entre tipos de ciclo.** Para cada serie se fechan los giros sobre la tasa, el desvío y el nivel. Los giros del mismo tipo separados por hasta 18 meses se agrupan en una fila, con el ciclo de crecimiento como ancla.

## Construcción de las series

El script `scripts/construir_datos.py` lee los archivos de `data/raw/` y aplica, en orden:

1. **Desacumulación.** La DNAP publica la recaudación y la ejecución presupuestaria **acumuladas en el año**. El monto de cada trimestre es la diferencia entre acumulados consecutivos, *M(q) = A(q) − A(q − 1)*, con *A(0) = 0*. Las unidades (miles o millones de pesos, según el archivo) se uniforman en millones.
2. **Deflactor.** Se empalma el IPIM nivel general del INDEC:
   - la base 1993 llega hasta octubre de 2015;
   - el IPIM con base diciembre de 2015 = 100 empieza en ese mes;
   - el INDEC no publicó noviembre de 2015, así que noviembre y diciembre de ese año se cubren con las variaciones del IPC de la Ciudad de Buenos Aires (+1,95 % y +3,92 %).

   El índice resultante se normaliza con promedio 2025 = 1. El trimestral es el promedio de los meses.
3. **Precios constantes.** *x real(t) = x nominal(t) / P(t)*, en pesos del promedio de 2025.
4. **Desestacionalización.** STL robusto (Cleveland et al., 1990) sobre el logaritmo de las series reales, con período 4 (trimestral) o 12 (mensual) y ventana estacional de 2·período + 1. El empleo ya viene desestacionalizado por la fuente.
5. **Ventana común.** Las cuatro series se recortan entre enero de 2011 y el último mes cubierto por todas.

El script también verifica que no falten trimestres, que todos los montos desacumulados sean positivos (un monto negativo delataría un cambio de unidades no detectado) y que el deflactor cubra todos los períodos.

## Estructura del repositorio

```
.
├── ciclo-rionegro.html                    # Visor completo (HTML + CSS + JavaScript + ECharts + datos)
├── screenshot-visor.png          # Captura usada en este documento
├── data/
│   ├── series.json               # Series procesadas (también incrustadas en index.html)
│   └── raw/                      # Datos crudos tal como se extrajeron de las fuentes
│       ├── api_mensual.csv               # Empleo (s.e. y original), IPIM base 1993 y dic-2015, IPC CABA
│       ├── salario_rn_mensual.csv        # Remuneración promedio corriente, Río Negro
│       ├── iibb_rn_trim_acumulado.csv    # IIBB acumulado en el año, con archivo y hoja de origen
│       └── gasto_rn_trim_acumulado.csv   # Gasto total APNF acumulado en el año, con archivo de origen
├── scripts/
│   └── construir_datos.py        # Desacumulación, empalme del IPIM, deflactación, STL e incrustación
├── requirements.txt              # Dependencias del script (pandas, numpy, statsmodels)
├── README.md                     # Este documento
└── LICENSE                       # Licencia MIT
```

`ciclo-rionegro.html` es un **único archivo autocontenido**: funciona abierto con doble clic, sin servidor ni conexión, y puede subirse tal cual a GitHub Pages o al aula virtual. Solo las tipografías se descargan de Google Fonts; sin conexión se usan las del sistema.

### Actualización de los datos

La actualización es **manual**, porque la DNAP publica planillas con formatos que cambian entre años. Se agregan las filas nuevas a los CSV de `data/raw/` y se regenera la página:

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/construir_datos.py --incrustar
```

| Archivo | Dónde se obtiene | Qué copiar |
|---|---|---|
| `api_mensual.csv` | API de Series de Tiempo: `154.2_RNEGROGRO_S_0_0_9`, `154.1_RNEGROGRO_C_0_0_9`, `106.3_I1NG_1993_M_23`, `448.1_NIVEL_GENERAL_0_0_13_46`, `193.1_NIVEL_GENERAL_JULI_0_13` | Los meses nuevos de cada columna |
| `salario_rn_mensual.csv` | OEDE, *Estadísticas e indicadores regionales*, planilla «Remuneraciones por provincia, serie mensual a 2 dígitos», hoja «Río Negro», fila «Total» | Los meses nuevos |
| `iibb_rn_trim_acumulado.csv` | DNAP, *Recursos Tributarios de Origen Provincial (TOP)*, información trimestral: fila «Río Negro», columna «Ingresos Brutos» de cada hoja (I TRIM, ACUM II TRIM, …) | El acumulado y la unidad que indica el encabezado (miles o millones) |
| `gasto_rn_trim_acumulado.csv` | DNAP, *Ejecuciones presupuestarias – APNF*, consolidado trimestral acumulado: columna «Río Negro», fila «Gastos totales (II+V)» | El acumulado y la unidad |

Los identificadores de la API y los nombres de las planillas pueden cambiar: conviene verificarlos antes de cada actualización. La DNAP revisa las ejecuciones provisorias, por lo que los últimos trimestres del gasto pueden modificarse.

## Stack técnico

- **JavaScript vanilla** (sin frameworks ni transpilación). Es el mismo núcleo de cálculo de [Ciclos de la economía argentina](https://fcontiggiani.github.io/ciclo-argentina/):
  - el filtro HP, resuelto con una factorización LDLᵀ de banda;
  - el filtro de Hamilton y las tendencias polinómicas, por mínimos cuadrados;
  - la media móvil centrada;
  - el fechado de Bry–Boschan.
- **[Apache ECharts](https://echarts.apache.org/) 5.4.3**, embebido en `index.html`.
- **Google Fonts**: IBM Plex Sans Condensed (títulos), IBM Plex Sans (interfaz), IBM Plex Mono (valores numéricos).
- **Python ≥ 3.10** con `pandas`, `numpy` y `statsmodels` (STL) para construir las series.
- Sin dependencias de servidor: todo el cálculo se ejecuta en el navegador del usuario.

## Notas metodológicas y limitaciones conocidas

- **Ventana corta.** Quince años contienen pocos ciclos completos. Las medianas de los desfases y las duraciones medias se calculan sobre pocos episodios y deben leerse con cautela.
- **Deflactor.** El IPIM mide precios mayoristas nacionales, no los precios que enfrentan los hogares ni el gobierno de Río Negro.
  - Su uso como deflactor del salario y del gasto da una medida del poder de compra en términos de bienes, no del salario real en sentido estricto. El IPC de la región Patagonia (INDEC, desde diciembre de 2016) sería la alternativa natural para las remuneraciones.
  - Los índices de precios del INDEC del período 2007–2015 fueron objeto de la emergencia estadística de 2016, y el empalme de noviembre y diciembre de 2015 con el IPC CABA es un supuesto propio.
  - Un error en el deflactor se traslada como un salto de nivel común a las tres series nominales.
- **Desestacionalización.** Se usa STL por simplicidad y reproducibilidad; no reemplaza un ajuste con X-13ARIMA-SEATS con tratamiento de efectos calendario y diagnóstico de estabilidad. La remuneración incluye el SAC (junio y diciembre), cuya estacionalidad absorbe STL. Cambios en el calendario de pago del aguinaldo pueden dejar residuos.
- **Empleo.** La serie desestacionalizada muestra una caída abrupta en enero de 2016 que conviene contrastar con la serie original y con la documentación del SIPA antes de interpretarla como un episodio económico.
- **Gasto.** Es gasto devengado y provisorio de la APNF; incluye transferencias a municipios y servicios de la deuda.
- **IIBB.** La recaudación responde a cambios de alícuotas, regímenes de retención y moratorias, no solo al nivel de actividad.
- **Fechado simplificado.** El algoritmo omite el suavizado previo de Bry–Boschan; las fechas no sustituyen a una cronología oficial.

## Referencias

Bry, G., & Boschan, C. (1971). *Cyclical analysis of time series: Selected procedures and computer programs*. National Bureau of Economic Research.

Burns, A. F., & Mitchell, W. C. (1946). *Measuring business cycles*. National Bureau of Economic Research.

Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, *6*(1), 3–73.

Hamilton, J. D. (2018). Why you should never use the Hodrick-Prescott filter. *Review of Economics and Statistics*, *100*(5), 831–843.

Harding, D., & Pagan, A. (2002). Dissecting the cycle: A methodological investigation. *Journal of Monetary Economics*, *49*(2), 365–381.

Hodrick, R. J., & Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. *Journal of Money, Credit and Banking*, *29*(1), 1–16.

Ravn, M. O., & Uhlig, H. (2002). On adjusting the Hodrick-Prescott filter for the frequency of observations. *Review of Economics and Statistics*, *84*(2), 371–376.

Zarnowitz, V., & Ozyildirim, A. (2006). Time series decomposition and measurement of business cycles, trends and growth cycles. *Journal of Monetary Economics*, *53*(7), 1717–1739.

## Autoría

Federico Contiggiani — Universidad Nacional de Río Negro (UNRN)

## Licencia

El código se distribuye bajo licencia [MIT](https://opensource.org/licenses/MIT) (véase `LICENSE`). Apache ECharts, incluido en `index.html`, se distribuye bajo licencia [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Los datos pertenecen a sus fuentes (SIPA-OEDE, DNAP, INDEC e IDECBA) y se redistribuyen con fines académicos, citando su origen.
