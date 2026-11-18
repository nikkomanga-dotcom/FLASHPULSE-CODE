"""Static, curated content for FlashPulse (fallbacks, editorial pills, glossary).

Everything that is *not* fetched live lives here, so server.py stays about routes.
"""

# ── Demo news (shown ONLY when no live news is available, always flagged demo=True) ──
DEMO_NEWS = [
    {
        "id": "n-nvda-earnings",
        "title": "Nvidia batte le attese: ricavi record trainati dai data center",
        "bullets": [
            "Ricavi del trimestre a 42,1 mld $, sopra il consenso di 40,2 mld",
            "Segmento data center +112% su anno, domanda AI ancora in espansione",
            "Guidance trimestre successivo oltre le stime: titolo +6% nell'after-hours"
        ],
        "impact": 9,
        "tags": ["#Tech", "#Semiconduttori", "#AI"],
        "domino": "Nvidia sorprende → semiconduttori europei (ASML, STM) tirano → fornitori di energia e cloud beneficiano della spesa capex AI",
        "sources": ["Reuters", "Bloomberg", "SEC Filing"],
        "ticker": "NVDA",
        "region": "USA",
        "category": "markets",
        "age_minutes": 45,
        "deep_dive": {
            "analysis": "I conti di Nvidia confermano che la spesa capex delle Big Tech sull'infrastruttura AI non sta rallentando. Hyperscaler come Microsoft, Meta, Google e Amazon hanno collettivamente guidato oltre 230 mld $ di capex 2025, e Nvidia ne cattura circa il 70% nel segmento GPU. La guidance implica margini lordi oltre il 73%.",
            "bull": "Se la domanda AI resta a questi ritmi, Nvidia può superare i 200 mld $ di ricavi 2026 con utili diluiti vicini a 5 $/azione, spingendo il settore semiconduttori verso nuovi massimi.",
            "bear": "Un rallentamento del capex AI (anche solo -15%) comprimerebbe multipli già a 35x utili attesi. Rischio concentrazione clienti: top 4 clienti pesano oltre il 40% dei ricavi.",
            "history": {
                "title": "Cisco 1999-2001: quando l'infrastruttura mangiò la bolla",
                "body": "Cisco dominava gli switch durante il boom internet con quote simili a quelle attuali di Nvidia nelle GPU AI. Il titolo guadagnò il 1.300% in 5 anni per poi perdere l'88% quando il capex telco si fermò. La lezione: anche con fondamentali reali, la concentrazione del capex su pochi clienti crea fragilità nei cicli discendenti."
            }
        }
    },
    {
        "id": "n-fed-cut",
        "title": "La Fed taglia i tassi di 25pb ma Powell gela i mercati",
        "bullets": [
            "Range target fondi federali: 4,25%–4,50% (-25pb)",
            "Powell: \"Ulteriori tagli non sono su un percorso prestabilito\"",
            "Dot plot 2026 rivisto a 2 tagli (dai 4 previsti a settembre)"
        ],
        "impact": 10,
        "tags": ["#Tassi", "#Macro", "#USA"],
        "domino": "Hawkish cut della Fed → curva USA si appiattisce → dollaro forte → pressione su mercati emergenti e materie prime",
        "sources": ["Federal Reserve", "Wall Street Journal", "Financial Times"],
        "ticker": None,
        "region": "USA",
        "category": "macro",
        "age_minutes": 120,
        "deep_dive": {
            "analysis": "Il taglio è stato ampiamente scontato, ma la revisione del dot plot da 4 a 2 tagli per il 2026 è il vero shock. Powell ha segnalato che l'inflazione core PCE a 2,8% resta troppo lontana dal target. Il mercato ora prezza il primo taglio successivo solo a giugno 2026.",
            "bull": "Economia USA resiliente, utili aziendali in crescita del 12% e PIL sopra il 2,5%: un ciclo di tagli lento può convivere con un bull market dei titoli a grande capitalizzazione.",
            "bear": "Tassi reali oltre il 2% compressero storicamente i multipli PE. Nel 2007-2008 un ciclo di tagli iniziato troppo tardi non impedì la recessione. Attenzione a leveraged loans e commercial real estate.",
            "history": {
                "title": "1994: l'anno in cui la Fed sorprese i mercati",
                "body": "Greenspan alzò i tassi di 300pb in 12 mesi dopo averli tenuti fermi. L'S&P 500 perse quasi il 10% intra-anno e il mercato obbligazionario visse il peggior anno dal 1927. Il caso attuale è opposto ma simmetrico: il mercato aveva prezzato troppo dovish, la Fed sta correggendo le aspettative."
            }
        }
    },
    {
        "id": "n-opec-cut",
        "title": "OPEC+ estende i tagli alla produzione fino a giugno 2026",
        "bullets": [
            "Riduzione volontaria di 2,2 mln barili/giorno confermata",
            "Arabia Saudita e Russia guidano il fronte dei prezzi alti",
            "Brent +3,2% a 76 $, WTI vicino a 73 $"
        ],
        "impact": 8,
        "tags": ["#Energia", "#OPEC", "#Inflazione"],
        "domino": "OPEC+ tiene i prezzi alti → benzina più cara in Europa → CPI armonizzato sotto pressione → BCE più cauta sui tagli",
        "sources": ["Reuters", "Il Sole 24 Ore", "Bloomberg"],
        "ticker": "WTI",
        "region": "Medio Oriente",
        "category": "energy",
        "age_minutes": 180,
        "deep_dive": {
            "analysis": "Il taglio prolungato riflette la paura OPEC+ che il petrolio USA (shale) e il rallentamento cinese possano spingere i prezzi sotto i 70 $. Breakeven fiscale saudita: 85 $/barile. I margini di raffinazione europei si comprimono mentre le compagnie integrate (Shell, ENI, TotalEnergies) beneficiano.",
            "bull": "Prezzi sopra 80 $ sostengono utili delle major energetiche europee, buyback record e dividendi in aumento. ENI può distribuire oltre 5 mld € nel 2026.",
            "bear": "Domanda cinese fiacca (PIL 4,5%) e crescita EV globale potrebbero disaccoppiare i prezzi dal taglio produzione. Rischio di glut nel H2 2026 se gli USA aumentano output oltre 14 mln b/g.",
            "history": {
                "title": "1986: il crollo del petrolio che ridefinì la geopolitica",
                "body": "L'Arabia Saudita, stufa di sostenere i prezzi mentre altri sforavano le quote, aprì i rubinetti. Il petrolio passò da 30 $ a 10 $ in 6 mesi, l'URSS perse metà delle entrate, boom USA. Oggi lo scenario inverso: coesione OPEC+ per difendere i prezzi, ma la lezione è che la disciplina del cartello è fragile."
            }
        }
    },
    {
        "id": "n-taiwan",
        "title": "Taiwan: Cina intensifica esercitazioni navali attorno all'isola",
        "bullets": [
            "90 velivoli militari e 15 navi rilevate nelle 24 ore",
            "USA invia portaerei Nimitz nello Stretto",
            "TSMC conferma continuità produttiva, titoli chip volatili"
        ],
        "impact": 9,
        "tags": ["#Geopolitica", "#Semiconduttori", "#Cina"],
        "domino": "Tensione Taiwan → premio di rischio su TSMC → prezzi chip più alti → pressione su smartphone, auto, data center a livello globale",
        "sources": ["Reuters", "Financial Times", "Nikkei Asia"],
        "ticker": "TSM",
        "region": "Asia",
        "category": "geopolitics",
        "age_minutes": 60,
        "deep_dive": {
            "analysis": "TSMC produce il 92% dei chip avanzati sotto 7nm. Un blocco navale (non invasione) sarebbe sufficiente a paralizzare le forniture per settimane. Il governo di Taipei stima 3 mesi di scorte, mentre Apple, Nvidia e AMD hanno piani di contingenza su Arizona e Giappone.",
            "bull": "Nessuna invasione imminente: le esercitazioni sono rituali politici pre-elettorali. Il mercato tende a sconvalutare questi eventi dopo 2-3 settimane.",
            "bear": "Un errore di calcolo può scatenare una crisi tipo 1962 (Cuba). Simulazioni CSIS indicano shock del PIL globale fino al -5% in caso di blocco prolungato.",
            "history": {
                "title": "1996: la terza crisi dello Stretto di Taiwan",
                "body": "Cina lanciò missili vicino a Taiwan per intimidire le elezioni. Clinton rispose con due gruppi di portaerei. Mercati scesero del 7% in 3 settimane poi recuperarono. La lezione: la deterrenza USA funziona ma la retorica militare pesa sul premio di rischio asset asiatici."
            }
        }
    },
    {
        "id": "n-ecb-pause",
        "title": "BCE pausa su tasso di deposito al 2,75%, inflazione eurozona stabile",
        "bullets": [
            "Decisione unanime del Governing Council",
            "Lagarde: \"Dati salariali permettono pazienza\"",
            "Spread BTP-Bund stabile a 128pb"
        ],
        "impact": 7,
        "tags": ["#BCE", "#Eurozona", "#Tassi"],
        "domino": "BCE pausa → euro stabile su dollaro → esportatori italiani (lusso, automotive) mantengono competitività ma pressione sui margini resta",
        "sources": ["BCE", "Il Sole 24 Ore", "Reuters"],
        "ticker": None,
        "region": "Eurozona",
        "category": "macro",
        "age_minutes": 240,
        "deep_dive": {
            "analysis": "La BCE segue la Fed con prudenza. Con inflazione headline al 2,3% e core al 2,7%, la pausa è giustificata. Lagarde ha evitato di fissare un percorso, lasciando ampia opzionalità. Mercato prezza prossimo taglio a marzo 2026.",
            "bull": "Pausa consente convergenza verso target 2% senza stroncare la timida ripresa tedesca (PMI manifatturiero 46,5, in miglioramento).",
            "bear": "Divergenza con Fed restrittiva pesa sulle banche europee (NIM compressi). Rischio ricadute su credito a PMI italiane.",
            "history": {
                "title": "2011: l'errore BCE di Trichet",
                "body": "Durante la crisi del debito europeo la BCE alzò i tassi 2 volte prima di invertire rotta pochi mesi dopo. Risultato: recessione double-dip. Oggi il contesto è migliore ma la lezione è non combattere troppo a lungo l'ultimo nemico."
            }
        }
    },
    {
        "id": "n-redsea",
        "title": "Mar Rosso: attacchi Houthi fanno schizzare i noli container +18%",
        "bullets": [
            "Rotte Asia-Europa deviate via Capo di Buona Speranza",
            "Noli spot su Shanghai-Genova a 4.850 $/TEU",
            "Maersk e MSC confermano tempi di transito +14 giorni"
        ],
        "impact": 8,
        "tags": ["#SupplyChain", "#Shipping", "#Inflazione"],
        "domino": "Mar Rosso bloccato → noli alti → costi import europei ↑ → pressione su inflazione beni, settori auto e retail penalizzati",
        "sources": ["Reuters", "Financial Times", "Lloyd's List"],
        "ticker": None,
        "region": "Medio Oriente",
        "category": "geopolitics",
        "age_minutes": 150,
        "deep_dive": {
            "analysis": "Il 12% del traffico mondiale passa dal Canale di Suez. Deviazione da Capo di Buona Speranza aggiunge 3.500 miglia e 10-14 giorni. Aziende come IKEA e Decathlon hanno già lanciato alert su ritardi scorte Q1 2026.",
            "bull": "Compagnie container (Maersk, Hapag-Lloyd) beneficiano di tariffe spot elevate. Guadagni trimestrali potrebbero sorprendere.",
            "bear": "Effetto secondo giro: inflazione beni europei +0,4-0,6% su 6 mesi. BCE costretta a rinviare tagli ulteriori.",
            "history": {
                "title": "2021: lo Ever Given e il blocco di Suez",
                "body": "6 giorni di blocco causarono 400 navi in coda e shock da 9 mld $/giorno al commercio globale. L'episodio attuale è strutturalmente peggiore: non è un incidente ma un'operazione militare prolungata. Impatti cumulati già superano quelli del 2021."
            }
        }
    },
    {
        "id": "n-tesla",
        "title": "Tesla taglia i prezzi del Model Y in Europa: -8% dopo weekend record",
        "bullets": [
            "Nuovo prezzo di listino Model Y RWD: 41.990 €",
            "Mossa per contrastare BYD e Volkswagen",
            "Analisti vedono rischio di margini sotto 15%"
        ],
        "impact": 6,
        "tags": ["#Auto", "#EV", "#Europa"],
        "domino": "Tesla sconta → guerra prezzi EV si intensifica → Stellantis e VW costretti a rispondere → compressione margini in tutto il settore",
        "sources": ["Bloomberg", "Il Sole 24 Ore", "Automotive News"],
        "ticker": "TSLA",
        "region": "Europa",
        "category": "markets",
        "age_minutes": 300,
        "deep_dive": {
            "analysis": "Tesla gioca la carta del volume per difendere la quota in Europa, scesa al 17% dei BEV venduti (dal 23% 2024). Il margine lordo auto, già a 17%, rischia di scendere sotto il 14% nel Q1.",
            "bull": "Volumi più alti preparano l'ecosistema (rete Supercharger, FSD) per il robotaxi previsto 2027.",
            "bear": "Senza breakthrough autonomia, Tesla si trasforma in un auto maker a margine da auto maker. Le valutazioni attuali non reggono questo scenario.",
            "history": {
                "title": "Ford anni '20: il modello T e la trappola del volume",
                "body": "Ford dominava con il Model T grazie a prezzi aggressivi. Negli anni '20 GM, con brand multipli e modelli differenziati, erose la sua quota. La lezione: competere solo sul prezzo è un'arma a doppio taglio quando emergono alternative differenziate (BYD, Rivian, Lucid)."
            }
        }
    },
    {
        "id": "n-china-stimulus",
        "title": "Cina annuncia nuovo pacchetto stimolo: 2.800 miliardi yuan per il 2026",
        "bullets": [
            "Focus su consumi interni e settore immobiliare",
            "Deficit pubblico allargato al 4% del PIL",
            "CSI 300 +3,1%, yuan si apprezza vs dollaro"
        ],
        "impact": 8,
        "tags": ["#Cina", "#Stimolo", "#Immobiliare"],
        "domino": "Pechino stimola → lusso italiano (LVMH, Ferragamo) beneficia → materie prime (rame, ferro) risalgono → sentiment emergenti positivo",
        "sources": ["Reuters", "Caixin", "Financial Times"],
        "ticker": None,
        "region": "Cina",
        "category": "macro",
        "age_minutes": 420,
        "deep_dive": {
            "analysis": "Il pacchetto è il più aggressivo dal 2020. Si affianca ai tagli dei tassi PBOC e mira a stabilizzare il settore immobiliare, in crisi strutturale. Impatto sul PIL atteso: +0,8-1,2%.",
            "bull": "Ripresa consumi cinesi riporterebbe growth globale al 3,2% 2026, con benefici forti su export italiano e tedesco.",
            "bear": "Stimulus fatiscenti: 4 pacchetti dal 2023 non hanno invertito il trend demografico-immobiliare. Debito totale Cina al 320% del PIL è un peso strutturale.",
            "history": {
                "title": "Giappone 1990-2010: le \"lost decades\" dello stimolo infinito",
                "body": "Dopo lo scoppio della bolla immobiliare, il Giappone lanciò decine di pacchetti fiscali e tassi a zero. Risultato: debito pubblico al 240% del PIL e crescita media 0,8%. La Cina rischia una traiettoria simile se non ristruttura il settore immobiliare."
            }
        }
    }
]

# ── Big Tech: static fallback + qualitative detail ──
BIG_TECH = [
    {"ticker": "NVDA", "name": "Nvidia", "sector": "Semiconduttori", "revenue_ttm": 118.2, "revenue_growth": 94.5, "pe": 37.4, "verdict": "bullish", "note": "Dominio AI GPU, margini record"},
    {"ticker": "AAPL", "name": "Apple", "sector": "Tech Hardware", "revenue_ttm": 391.0, "revenue_growth": 2.0, "pe": 31.2, "verdict": "neutral", "note": "iPhone 16 vendite tiepide, servizi solidi"},
    {"ticker": "MSFT", "name": "Microsoft", "sector": "Software & Cloud", "revenue_ttm": 254.2, "revenue_growth": 15.0, "pe": 33.1, "verdict": "bullish", "note": "Azure AI e Copilot driver principali"},
    {"ticker": "GOOGL", "name": "Alphabet", "sector": "Internet", "revenue_ttm": 344.0, "revenue_growth": 13.0, "pe": 24.8, "verdict": "bullish", "note": "Search resiste, Gemini sorprende"},
    {"ticker": "META", "name": "Meta", "sector": "Social Media", "revenue_ttm": 164.0, "revenue_growth": 21.0, "pe": 26.5, "verdict": "bullish", "note": "AI ads monetizzano, Reality Labs ancora in perdita"},
    {"ticker": "TSLA", "name": "Tesla", "sector": "EV & AI", "revenue_ttm": 97.6, "revenue_growth": -1.2, "pe": 78.2, "verdict": "bearish", "note": "Guerra prezzi EU, margini sotto pressione"},
    {"ticker": "ASML", "name": "ASML", "sector": "Semiconduttori EU", "revenue_ttm": 28.3, "revenue_growth": 1.5, "pe": 38.5, "verdict": "neutral", "note": "Backlog solido ma export Cina ridotto"},
]

BIG_TECH_DETAIL = {
    "NVDA": {"description": "Produttore globale di GPU per data center, gaming e automotive. Domina il mercato chip AI con oltre il 90% di quota nei GPU per training.", "revenue_breakdown": [{"seg": "Data Center", "pct": 87}, {"seg": "Gaming", "pct": 9}, {"seg": "Automotive", "pct": 2}, {"seg": "Altro", "pct": 2}], "catalysts": ["Blackwell rollout", "Capex hyperscaler 2026", "Export China H200"], "risks": ["Concentrazione clienti (top 4 = 40%)", "Rivalità custom silicon MS/Google", "Rallentamento capex AI"]},
    "AAPL": {"description": "Ecosistema iPhone + servizi (App Store, iCloud, Apple TV+). Rendimento azionario guidato da buyback aggressivi.", "revenue_breakdown": [{"seg": "iPhone", "pct": 52}, {"seg": "Servizi", "pct": 23}, {"seg": "Wearables", "pct": 9}, {"seg": "Mac/iPad", "pct": 16}], "catalysts": ["Apple Intelligence", "Vision Pro v2", "India manufacturing scale"], "risks": ["Ciclo iPhone fiacco", "Antitrust App Store UE", "Esposizione Cina"]},
    "MSFT": {"description": "Software enterprise + Azure cloud + Copilot AI. Partner esclusivo OpenAI con investimento 13 mld $.", "revenue_breakdown": [{"seg": "Productivity (Office)", "pct": 33}, {"seg": "Intelligent Cloud (Azure)", "pct": 41}, {"seg": "More PC", "pct": 26}], "catalysts": ["Azure AI crescita >30%", "Copilot adoption enterprise", "Activision sinergie"], "risks": ["Compressione margini AI capex", "Rallentamento Office", "Rischio regolatorio"]},
    "GOOGL": {"description": "Search + YouTube + Google Cloud + Android. Gemini la sfida a ChatGPT; waymo sta scalando robotaxi.", "revenue_breakdown": [{"seg": "Search ads", "pct": 56}, {"seg": "YouTube ads", "pct": 10}, {"seg": "Google Cloud", "pct": 12}, {"seg": "Altro", "pct": 22}], "catalysts": ["Gemini 3 adozione", "Waymo espansione città", "AI Overviews monetizzazione"], "risks": ["Antitrust search USA", "Rottura contratto Apple default", "Cannibalizzazione AI su search"]},
    "META": {"description": "Facebook + Instagram + WhatsApp + Reality Labs (VR/AR). Advantage+ AI ads drive la monetizzazione.", "revenue_breakdown": [{"seg": "Family of Apps ads", "pct": 97}, {"seg": "Reality Labs", "pct": 3}], "catalysts": ["Advantage+ ROI ads", "Threads scala", "Llama open-source"], "risks": ["Reality Labs perde 16 mld $/anno", "Regolamentazione minori UE/USA", "Ciclo capex AI pesante"]},
    "TSLA": {"description": "EV + energy storage + Full Self Driving + Optimus robot umanoide. Roadmap robotaxi 2026-27.", "revenue_breakdown": [{"seg": "Auto", "pct": 82}, {"seg": "Energy + Services", "pct": 18}], "catalysts": ["FSD V13 rollout", "Cybercab unveiling", "Optimus produzione"], "risks": ["Guerra prezzi EV Cina", "Margini sotto 15%", "Controversie governance"]},
    "ASML": {"description": "Monopolio litografia EUV per chip sotto 7nm. Cliente chiave TSMC e Samsung.", "revenue_breakdown": [{"seg": "EUV sistemi", "pct": 55}, {"seg": "DUV sistemi", "pct": 30}, {"seg": "Service", "pct": 15}], "catalysts": ["Backlog oltre 36 mld €", "High-NA EUV ramp", "Domanda AI chip 2026-27"], "risks": ["Restrizioni export Cina", "Ciclicità memory", "Dipendenza da pochi clienti"]},
}

# ── Scenarios (editorial hypotheses, not predictions) ──
SCENARIOS = [
    {"name": "Soft Landing", "probability": 55, "narrative": "Inflazione USA scende al 2,2%, Fed taglia 2 volte, utili crescono 10%, S&P 500 target 6500.", "assets": "Azioni large cap USA, tech qualitativo, oro come hedge"},
    {"name": "Stagflazione Light", "probability": 25, "narrative": "Inflazione sticky al 3%, PIL 1,2%, Fed in pausa prolungata, multipli compressi.", "assets": "Materie prime, energia, value europeo, cash"},
    {"name": "Hard Landing", "probability": 15, "narrative": "Recessione USA Q3 2026, utili -8%, Fed taglia 150pb, bond rally.", "assets": "Treasury lunghi, oro, difensivi (utilities, healthcare)"},
    {"name": "Melt-up AI", "probability": 5, "narrative": "Produttività AI +2% annuo, utili tech +25%, Nasdaq target 25.000.", "assets": "Semiconduttori, software, infrastruttura cloud"},
]

# ── Learn ──
LEARN_TERMS = [
    {"term": "Spread BTP-Bund", "short": "Differenza di rendimento fra titoli italiani e tedeschi.", "detail": "Misura in punti base (pb) quanto in più paga il debito italiano rispetto a quello tedesco (ritenuto 'risk-free' nell'eurozona). Uno spread a 200pb significa che il BTP rende 2 punti percentuali in più del Bund stesso maturity. Più alto = più rischio percepito su Italia.", "example": "Se lo spread passa da 120 a 180pb in una settimana, il mercato teme instabilità politica o fiscale italiana.", "category": "Macro"},
    {"term": "Quantitative Easing (QE)", "short": "Banca centrale compra bond per abbassare i tassi lunghi e immettere liquidità.", "detail": "Quando i tassi sono già a zero, la banca centrale compra titoli di stato e corporate dal mercato aperto. Questo spinge i prezzi dei bond su, i rendimenti giù, e libera liquidità che banche e investitori mettono in azioni e credito.", "example": "La BCE lanciò il QE nel 2015 (Draghi) comprando 60 mld €/mese per 3 anni per combattere la deflazione.", "category": "Macro"},
    {"term": "Dot Plot", "short": "Grafico Fed con la previsione di ogni membro FOMC sui tassi futuri.", "detail": "Ogni trimestre, i 19 membri del FOMC scrivono dove pensano che saranno i Fed Funds tra 1, 2, 3 anni e nel lungo periodo. Il grafico a punti (dot plot) mostra la dispersione. La mediana è quello che il mercato segue di più.", "example": "Se il dot plot di dicembre sposta la mediana 2026 da 3,5% a 4,0%, significa Fed più hawkish e azioni a leva tassi (growth, REIT) soffrono.", "category": "Macro"},
    {"term": "Bull vs Bear", "short": "Toro = mercati in salita, Orso = in discesa.", "detail": "Metafora di Wall Street: il toro attacca dal basso verso l'alto (prezzi su), l'orso dall'alto verso il basso (prezzi giù). 'Bull case' significa scenario rialzista, 'bear case' scenario ribassista. Un 'bear market' tecnico è un calo dai massimi superiore al 20%.", "example": "Il crollo 2008 fu un bear market: S&P 500 -57%. Il 2020-2022 fu un bull market: +114% dai minimi Covid.", "category": "Mercati"},
    {"term": "Effetto Domino Macro", "short": "Catena causa-effetto fra un evento e settori apparentemente lontani.", "detail": "Un singolo evento (es. taglio petrolio) si propaga: materie prime ↑ → inflazione ↑ → banche centrali più caute → tassi alti più a lungo → settori sensibili ai tassi (real estate, tech growth) soffrono. Imparare a vederlo è il salto da notizia a investimento.", "example": "OPEC+ taglia 2 mln b/g → benzina EU cara → CPI europeo sopra target → BCE rinvia tagli → BTP soffre, lusso italiano dipendente dalla Cina pure.", "category": "Strategia"},
    {"term": "Geopolitical Risk Premium", "short": "Extra-rendimento che il mercato chiede per asset esposti a rischio politico.", "detail": "Quando aumenta la tensione geopolitica (guerra, sanzioni, blocchi navali), gli investitori chiedono un premio più alto per detenere asset esposti. Risultato: valuta debole, borsa in calo, oro e dollaro salgono.", "example": "Dopo l'invasione Ucraina 2022, il rublo perse 40%, oro +12%, S&P 500 -13% nei primi 60 giorni.", "category": "Geopolitica"},
    {"term": "Multiplo P/E", "short": "Quante volte gli utili annuali costa un'azione.", "detail": "Price/Earnings = Prezzo azione / Utile per azione. Un P/E 20 vuol dire che paghi 20 € per ogni € di utile annuo. Settori growth hanno P/E 30-50, value 8-15. Serve a confrontare aziende dello stesso settore o la stessa azienda nel tempo.", "example": "Nvidia a P/E 35 sembra caro, ma se gli utili crescono del 50%/anno è sostenibile. Apple a P/E 30 con utili flat è più preoccupante.", "category": "Mercati"},
    {"term": "Supply Chain", "short": "Catena globale di fornitori che porta un prodotto dallo scavo alla casa.", "detail": "Un iPhone usa 400+ fornitori in 40+ paesi. Un blocco di uno snodo (Suez, Taiwan, Panama) fa ritardare la consegna globale per settimane. Le aziende che sanno gestirla (Apple, Zara) battono i competitor.", "example": "Blocco Ever Given Suez 2021: 400 navi in coda, 9 mld $/giorno di commercio bloccato. Impatto inflazionistico duraturo.", "category": "Supply Chain"},
    {"term": "Yield Curve Inversion", "short": "Quando i tassi corti sono più alti dei tassi lunghi.", "detail": "Normalmente i bond a 10 anni rendono più di quelli a 2 anni (rischio tempo). Quando si inverte, significa che il mercato prevede recessione: la Fed dovrà tagliare presto. Ha preceduto tutte le recessioni USA dal 1970.", "example": "L'inversione 2-10 iniziò nel luglio 2022. La recessione ancora non è arrivata, segno di quanto il ciclo attuale sia atipico.", "category": "Macro"},
    {"term": "Fear & Greed Index", "short": "Indicatore sintetico di sentiment del mercato (paura ↔ avidità).", "detail": "Calcolato come media di 7 fattori: volatilità, momentum, flussi safe-haven, bond demand, put/call ratio, breadth, junk bond. Va da 0 (panico totale) a 100 (euforia).", "example": "A marzo 2020 scese a 2 (massimo panico). Nel 2024 è salito a 80+ (euforia tech). Comprare a 20, vendere a 80.", "category": "Mercati"},
]

QUIZZES = [
    {"q": "Cosa misura lo spread BTP-Bund?", "options": ["Il PIL italiano vs tedesco", "Il differenziale di rendimento fra BTP italiani e Bund tedeschi", "Il cambio euro/dollaro", "Il prezzo del petrolio"], "correct": 1, "term": "Spread BTP-Bund"},
    {"q": "Un dot plot hawkish della Fed implica…", "options": ["Più tagli di tassi previsti", "Meno tagli di tassi previsti", "Nessun cambiamento ai tassi", "Un ritorno al QE"], "correct": 1, "term": "Dot Plot"},
    {"q": "Un bear market si definisce come un calo dai massimi di almeno…", "options": ["5%", "10%", "20%", "50%"], "correct": 2, "term": "Bull vs Bear"},
    {"q": "Se OPEC+ taglia la produzione, l'effetto domino più probabile è:", "options": ["Prezzi energia ↓ e inflazione ↓", "Prezzi energia ↑ e inflazione ↑", "Tassi ↓ immediatamente", "Nessun impatto macro"], "correct": 1, "term": "Effetto Domino Macro"},
    {"q": "Un yield curve inverted anticipa storicamente…", "options": ["Una bolla azionaria", "Una recessione", "Una crisi valutaria", "Un boom immobiliare"], "correct": 1, "term": "Yield Curve Inversion"},
]

QUIZZES += [
    {"q": "Cosa fa una banca centrale con il Quantitative Easing?", "options": ["Vende titoli di stato per ritirare liquidità", "Compra titoli per abbassare i tassi lunghi e immettere liquidità", "Alza i tassi di interesse", "Dà soldi direttamente ai cittadini"], "correct": 1, "term": "Quantitative Easing (QE)"},
    {"q": "Un P/E di 20 significa che…", "options": ["L'azienda cresce del 20% l'anno", "Paghi 20 € per ogni 1 € di utile annuo", "L'azione è salita del 20%", "Il dividendo è il 20%"], "correct": 1, "term": "Multiplo P/E"},
    {"q": "Un Fear & Greed Index vicino a 0 indica…", "options": ["Euforia", "Panico / paura estrema", "Mercato laterale", "Boom immobiliare"], "correct": 1, "term": "Fear & Greed Index"},
    {"q": "Quando aumenta la tensione geopolitica, di solito sale…", "options": ["La propensione al rischio", "L'oro, come bene rifugio", "Il prezzo dei bond spazzatura", "Il valore delle valute emergenti"], "correct": 1, "term": "Geopolitical Risk Premium"},
    {"q": "Perché un blocco a Suez può far salire l'inflazione?", "options": ["Riduce i salari", "Allunga i tempi di consegna e fa salire noli e costi di import", "Fa salire direttamente i tassi BCE", "Riduce la domanda di petrolio"], "correct": 1, "term": "Supply Chain"},
]

# ── Accadde oggi: eventi con data reale (day/month), scelti in base alla data odierna ──
HISTORY_EVENTS = [
    {"day": 24, "month": 10, "year": 1929, "title": "Giovedì nero: il crollo di Wall Street", "body": "Il 24 ottobre 1929 la Borsa di New York crollò tra il panico, aprendo la strada alla Grande Depressione. Cinque giorni dopo, il 29 ottobre, il Dow perse un altro 12%."},
    {"day": 19, "month": 10, "year": 1987, "title": "Black Monday", "body": "Il Dow Jones crollò del 22,6% in una sola seduta, la peggior giornata di sempre in percentuale. Dopo quel giorno furono introdotti i circuit breaker, ancora in uso oggi."},
    {"day": 9, "month": 11, "year": 1989, "title": "Cade il Muro di Berlino", "body": "La fine della divisione dell'Europa aprì l'era della globalizzazione: nuovi mercati, catene di fornitura globali e, più tardi, la nascita dell'euro."},
    {"day": 15, "month": 8, "year": 1971, "title": "Nixon chiude la convertibilità dollaro-oro", "body": "Con lo 'shock Nixon' gli USA sospesero la convertibilità del dollaro in oro: finì il sistema di Bretton Woods e nacque quello dei cambi flessibili che conosciamo."},
    {"day": 16, "month": 9, "year": 1992, "title": "Black Wednesday: la sterlina esce dallo SME", "body": "La Bank of England non riuscì a difendere la sterlina e abbandonò lo SME. Anche la lira uscì dal sistema. Soros guadagnò circa 1 mld $ scommettendo contro la sterlina."},
    {"day": 10, "month": 3, "year": 2000, "title": "Il picco della bolla dot-com", "body": "Il Nasdaq toccò i 5.048 punti. Servirono 15 anni per rivederli: nel frattempo l'indice era crollato di circa l'80%."},
    {"day": 1, "month": 1, "year": 2002, "title": "L'euro arriva nelle tasche degli europei", "body": "Banconote e monete in euro entrarono in circolazione in 12 paesi, sostituendo lire, marchi, franchi e altre valute nazionali."},
    {"day": 15, "month": 9, "year": 2008, "title": "Fallisce Lehman Brothers", "body": "La quarta banca d'investimento USA dichiarò bancarotta con circa 639 mld $ di attività: fu l'innesco della crisi finanziaria globale."},
    {"day": 6, "month": 5, "year": 2010, "title": "Flash Crash", "body": "Il Dow perse circa 1.000 punti in pochi minuti per via di vendite algoritmiche a catena, per poi recuperare gran parte del calo entro la chiusura."},
    {"day": 15, "month": 1, "year": 2015, "title": "La Svizzera abbandona il cambio fisso con l'euro", "body": "La banca centrale svizzera tolse il tetto al cambio euro-franco: il franco si apprezzò di circa il 30% in poche ore, causando perdite a molti broker."},
    {"day": 23, "month": 6, "year": 2016, "title": "Referendum Brexit", "body": "Il Regno Unito votò per lasciare l'UE. La sterlina scese ai minimi da oltre 30 anni e i mercati globali persero centinaia di miliardi in un giorno."},
    {"day": 11, "month": 3, "year": 2020, "title": "L'OMS dichiara la pandemia di Covid-19", "body": "I mercati crollarono: l'S&P 500 perse circa il 34% in 23 giorni. Poi arrivò la ripresa più rapida della storia, spinta da stimoli coordinati."},
    {"day": 20, "month": 4, "year": 2020, "title": "Il petrolio WTI va sotto zero", "body": "Per la prima volta nella storia il future sul WTI chiuse a prezzo negativo (circa -37 $ al barile): i depositi erano pieni e nessuno voleva ritirare il greggio."},
    {"day": 24, "month": 2, "year": 2022, "title": "La Russia invade l'Ucraina", "body": "Gas, grano e petrolio schizzarono, l'Europa avviò il distacco dall'energia russa e l'inflazione globale accelerò, costringendo le banche centrali ad alzare i tassi."},
]

_MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def format_event(ev: dict) -> dict:
    return {**ev, "date": f"{ev['day']} {_MESI[ev['month'] - 1]} {ev['year']}"}


# ── Radar geopolitico (curato): coordinate e regione macro vivono qui, non nel frontend ──
RADAR = [
    {"id": "taiwan", "region": "Stretto di Taiwan", "flag": "🇹🇼", "severity": 9, "theme": "Chip & deterrenza militare", "macro_region": "Asia", "lat": 23.7, "lng": 121.0,
     "keywords": ["taiwan", "tsmc", "taipei"],
     "summary": "Cina e Taiwan restano il punto di maggiore tensione per i chip: TSMC produce la gran parte dei semiconduttori più avanzati al mondo.",
     "history_title": "Crisi dello Stretto 1954, 1958, 1996", "history_body": "Tre crisi precedenti rientrate grazie alla deterrenza USA. Ogni volta i mercati asiatici hanno perso il 5-12%, recuperando in 3-6 mesi."},
    {"id": "redsea", "region": "Mar Rosso", "flag": "🇾🇪", "severity": 8, "theme": "Supply chain & shipping", "macro_region": "Medio Oriente", "lat": 15.5, "lng": 42.5,
     "keywords": ["red sea", "mar rosso", "houthi", "suez"],
     "summary": "Gli attacchi alle navi deviano il traffico dal Canale di Suez: viaggi più lunghi, noli più cari e pressione sui prezzi dei beni importati.",
     "history_title": "Guerra del Kippur 1973 e crisi petrolifera", "history_body": "Il blocco delle rotte generò uno shock energetico duraturo. Oggi l'impatto è su beni di consumo e auto più che sul petrolio."},
    {"id": "ukraine", "region": "Ucraina-Russia", "flag": "🇺🇦", "severity": 8, "theme": "Energia & grano", "macro_region": "Europa", "lat": 49.0, "lng": 32.0,
     "keywords": ["ukraine", "ucraina", "russia", "kyiv", "moscow"],
     "summary": "La guerra continua a pesare su gas, grano e sicurezza energetica europea, con attacchi alle infrastrutture e sanzioni in evoluzione.",
     "history_title": "Blocco di Berlino 1948-1949", "history_body": "Le contrapposizioni tra blocchi producono inflazione strutturale su materie prime chiave: rame, nickel, uranio, grano."},
    {"id": "iran", "region": "Iran-Israele", "flag": "🇮🇷", "severity": 7, "theme": "Petrolio & Stretto di Hormuz", "macro_region": "Medio Oriente", "lat": 32.0, "lng": 53.0,
     "keywords": ["iran", "israel", "israele", "hormuz", "tehran"],
     "summary": "Sanzioni e scontri reciproci tengono alto il rischio sul Golfo: dallo Stretto di Hormuz passa circa un quinto del petrolio mondiale.",
     "history_title": "Rivoluzione iraniana 1979", "history_body": "Il petrolio raddoppiò in 12 mesi, aprendo la recessione USA del 1980-82 e la stretta di Volcker."},
    {"id": "korea", "region": "Penisola Coreana", "flag": "🇰🇵", "severity": 5, "theme": "Nucleare & chip di memoria", "macro_region": "Asia", "lat": 40.0, "lng": 127.0,
     "keywords": ["north korea", "corea", "pyongyang", "seoul"],
     "summary": "Test missilistici intermittenti. Samsung e SK Hynix producono circa due terzi delle memorie DRAM mondiali: un rischio latente per l'AI.",
     "history_title": "Guerra di Corea 1950-1953", "history_body": "Ha creato un Sud iper-sviluppato e un Nord isolato. La concentrazione industriale sulle memorie è la vulnerabilità di oggi."},
    {"id": "africa", "region": "Sahel africano", "flag": "🇳🇪", "severity": 6, "theme": "Uranio & terre rare", "macro_region": "Africa", "lat": 17.6, "lng": 8.1,
     "keywords": ["niger", "mali", "burkina", "sahel"],
     "summary": "Instabilità politica in Niger, Mali e Burkina Faso: l'influenza si sposta da Francia a Russia e Cina, con l'uranio come posta in gioco.",
     "history_title": "Decolonizzazione 1960-70", "history_body": "Le risorse strategiche cambiano spesso di mano insieme al potere politico. L'uranio del Niger è critico per il nucleare francese."},
]

# ── Indicatori macro: valori mostrati solo se le fonti live non rispondono (con etichetta "dato di riferimento") ──
MACRO_FALLBACK = [
    {"id": "fedfunds", "name": "Tassi Fed (USA)", "value": "—", "trend": "flat", "delta": ""},
    {"id": "ecb", "name": "Tasso BCE (deposito)", "value": "—", "trend": "flat", "delta": ""},
    {"id": "cpi_us", "name": "Inflazione USA", "value": "—", "trend": "flat", "delta": ""},
    {"id": "hicp_ea", "name": "Inflazione Eurozona", "value": "—", "trend": "flat", "delta": ""},
    {"id": "ust10", "name": "Rendimento Treasury 10Y", "value": "—", "trend": "flat", "delta": ""},
    {"id": "btp10", "name": "Rendimento BTP 10Y", "value": "—", "trend": "flat", "delta": ""},
    {"id": "unrate", "name": "Disoccupazione USA", "value": "—", "trend": "flat", "delta": ""},
]


from datetime import datetime  # noqa: E402


def _day_distance(ev: dict, today: datetime) -> int:
    """Signed days from the event's anniversary to today (>0: anniversary already passed)."""
    best = None
    for y in (today.year - 1, today.year, today.year + 1):
        try:
            d = (today.date() - datetime(y, ev["month"], ev["day"]).date()).days
        except ValueError:
            continue
        if best is None or abs(d) < abs(best):
            best = d
    return best if best is not None else 9999


def pick_history(today: datetime) -> list[dict]:
    """All events, closest anniversary first. Each carries `days_ago` and `exact`."""
    out = []
    for ev in HISTORY_EVENTS:
        d = _day_distance(ev, today)
        out.append({**format_event(ev), "days_ago": d, "exact": d == 0})
    out.sort(key=lambda e: (abs(e["days_ago"]), e["days_ago"] < 0))
    return out


QUIZ_SIZE = 5


def daily_quiz(today: datetime) -> list[dict]:
    """A different, deterministic set of questions each day (rotating through the pool)."""
    pool = QUIZZES
    start = (today.toordinal() * QUIZ_SIZE) % len(pool)
    return [pool[(start + i) % len(pool)] for i in range(min(QUIZ_SIZE, len(pool)))]
