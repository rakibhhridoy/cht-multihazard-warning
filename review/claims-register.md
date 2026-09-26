# Claims register — every load-bearing claim, its current status, its source
Built 2026-09-22 from notes/01-21. THIS FILE WINS over any individual note where they conflict.
Status: SOLID = official/primary source in hand | PRESS = press only | INFER = our inference | OPEN = unconfirmed

## A. Forcing and rainfall
A1  June 2017 peak: 332 mm/24h Bandarban (FFWC Annual Report 2017, Table 2.3) and 343 mm/24h
    (BMD via Islam, Islam & Jeet 2021). Two independent gauge values. ................... SOLID
A2  Rain onset 12 June ~01:00 local (reanalysis) = "early morning of 12 June" (Islam 2021) .. SOLID
A3  Reanalysis underestimates the 2017 event: best_match 220.5 mm vs 343 gauge = 0.64x;
    era5 ~109 mm = ~0.32x. Correction multiplier 1.56 (anchored) ......................... SOLID
A4  ERA5-Land precipitation NOT served by Open-Meteo; "best_match" is an ERA5/ERA5-Land blend
    of undocumented composition. All reanalysis numbers are VIABILITY PROXIES; real study must
    use CDS ERA5-Land hourly + IMERG bracket. Do not cite Open-Meteo numbers in print ...... SOLID
A5  IMERG over Bangladesh +18 to +92% on extremes (opposite sign to ERA5-Land's >=20% under).
    The two bracket the truth -> use as the uncertainty analysis .......................... SOLID (lit)
    [SUPERSEDED by O2: the bracket fails for 2017. The ERA5 85 % claim is Y5]
A6  July 2026: Bandarban 309 mm (7-8 Jul, Daily Star/BMD); Rangamati 287 mm to 8 Jul (BDRCS/BMD);
    Chattogram Ambagan 329 mm to 06:00 9 Jul (BDRCS/BMD) .................................. SOLID
A7  Aug 2023: 44-89 mm/day prolonged; monthly to 10 Aug Bandarban 856, Chattogram 933,
    Rangamati 601 mm (NAWG/UNICEF) ......................................................... SOLID

## B. Observing network  [REVISED — notes/04 superseded by notes/17]
B1  GHCN-Daily: 10 Bangladesh stations; ZERO in the CHT; nearest two (Chattogram airport,
    Cox's Bazar) both at 3.7 m elevation. Verified BG block complete ....................... SOLID
B2  BWDB/FFWC ran **11 rainfall stations in the South Eastern Hill basin** in 2017 (FFWC AR 2017
    Table 2.3) plus river gauges Sangu x2, Matamuhuri x2, Halda x2, Feni, Karnaphuli ...... SOLID
B3  => The "gauge desert" is a desert of INTERNATIONALLY VISIBLE, METEOROLOGICALLY OWNED gauges.
    Hydrological gauges existed, inside the flood institution. Phrase it this way, always .. SOLID
B4  Rangamati has NO FFWC river station (none on Chengi/Maini/Kasalong/upper Karnaphuli);
    FFWC station list confirmed from live table + AR 2017 Table 3.4 ....................... SOLID
B5  Khan et al. (2012) used ONE BMD gauge (Chittagong) and "assumed... representative" ...... SOLID
B6  Gauge density vs a >=16-per-0.2deg benchmark (~1 per 30 km2): BMD-only (~3 in 13,300 km2)
    = ~150x below; BWDB's 11 SE-hill stations, IF all inside the CHT = ~40x below; over the
    whole SE hill basin (20-25k km2, assumed) = ~60-75x below; BMD+BWDB combined upper bound
    ~31x below. Quote as "40-150x depending on which network is counted", and say the BWDB
    station coordinates are not public — that itself is part of the finding ............... SOLID (range)

## C. Inventory
C1  Rabby & Li 730 records; 484 (66.3%) full date, 238 year-only, 8 blank ................. SOLID
C2  13/06/2017: 243 dated failures (Rangamati 146, Bandarban 91, Chittagong 6); median 59 m2 . SOLID
    [SUPERSEDED by Q2: 257 / Rangamati 160]
C3  Date field: "For Google Earth mapping, the date of the image was recorded" (Rabby & Li 2020) SOLID
C4  Rainfall date audit: 15 clusters/446 records; 4 SUSPECT dates = 83 records (18.6%);
    20/07/2017 Khagrachari (73) has ~20 mm on the date, 130 mm four days later, no documented
    event; Khagrachari IS documented in the June sequence (14, 18 June, Ramgarh) .......... SOLID
C5  FALSE POSITIVE: 11/06/2007 (the 127-death Chittagong disaster) flags WEAK at 33 mm.
    => audit produces FLAGS not deletions; reanalysis can miss real events ................ SOLID
C6  '13/06/207' malformed year, 14 records — resolve, don't drop ........................... RESOLVED (Q1)
C7  Cut-slope hypothesis for 20/07/2017: road/camp locations 51% vs 39% — weak, rejected .... SOLID

## D. June 2017 timing  [notes/13 SUPERSEDED by notes/14]
D1  Failure WINDOW, not point: night 12->13 Jun (asleep) -> "just after dawn" -> ~11:00
    (Manikchhari, soldiers). ~11 h progressive sequence .................................... SOLID (press)
    [SUPERSEDED by Q4: 02:30 to ~11:00, nine hours]
D2  Gauge-corrected threshold crossings vs window: empirical 24h (57.4) +31 to +42 h;
    deployed 24h (200) +14 to +25 h; deployed 72h (350) +3 to +14 h; deployed 3h (100) NEVER . SOLID*
    *3h/100 mm "never" holds under uniform scaling only — a smoothed local burst could have
    crossed it. Say so.
D3  ~17 h gap between empirical and deployed 24 h crossings = operational cost of the
    threshold discrepancy. Robust to uniform scaling ...................................... SOLID
    [SUPERSEDED by O5/Q5: 14-18 h]
D4  RETRACTED: "deployed thresholds set too high to use the window" (notes/13). Wrong after
    gauge correction. Do not use ............................................................ RETRACTED
D5  Regime: prolonged ~36 h moderate-intensity accumulation, failures 24-30 h in -> DELAYED
    regime signature (chi ~1-3), not synchronous. Preliminary; RSF inversion NOT done ...... INFER

## E. Thresholds
E1  Deployed (Chittagong City, 2 automated gauges): 100 mm/3h, 200 mm/24h, 350 mm/72h,
    presented as "to initiate landslide occurrence" (IntechOpen 10.5772/intechopen.74743) ... SOLID
    [station count SUPERSEDED by P8: four GSB stations, Chattogram and Cox's Bazar, 2015]
E2  Empirical (Cox's Bazar, Roy et al. 2022): T5 I=3.63D^-0.1313; 57.4 mm/24h; 130 mm/72h .. SOLID
E3  Deployed / empirical = 3.5x (24h), 2.7x (72h). Different districts, different constructions,
    NEITHER reports ROC/FAR. The absence of skill scores is the finding ................... SOLID
E4  RETRACTED: "no empirical I-D threshold exists for the region" — Roy et al. is one.
    Gap is CHT interior + validation + antecedent-state, not existence ..................... RETRACTED

## F. Flash flood, June 2017 (FFWC Annual Report 2017)
F1  Matamuhuri crossed DL at Lama and Chiringa 12 Jun; Sangu crossed + PEAKED at Bandarban
    13 Jun (16.60 m, +135 cm; 2017 peak vs 1988 record 16.80); Halda peaked 13 Jun ........ SOLID
F2  FFWC's own summary: "landslide in June at many places in the South East hilly region" .. SOLID
F3  FFWC flash flood forecast in 2017: "Experimental... April-May... North East region...
    13 stations" => NONE for the SE hills (Sec. 6.1) ...................................... SOLID
F4  DL datum: AR 2017 in mPWD (Sangu Bandarban DL 15.25); current table mMSL (DL 14.80).
    Compare cm-above-DL only .................................................................. SOLID

## G. Institutions, 2017
G1  No operational LEWS anywhere in Bangladesh; CDMP-II Cox's Bazar 2012 community-based;
    NGO efforts "sporadic... failed" (lit.) ................................................. SOLID (lit)
G2  Chittagong Metropolitan web-GIS LEWS published 2018 (after the event) ................... SOLID
G3  => June 2017: observing infrastructure existed for both hazards; warning function for
    neither; Rangamati had neither station nor forecast ................................... SOLID
G4  Operational date of the 2 Chittagong City gauges relative to June 2017 ................. OPEN
    [SUPERSEDED by P8: four stations set up 2015, "not yet functional" in 2018]

## H. August 2023
H1  Sangu at Bandarban 17.63 m = +283 cm DL, 7 Aug (FFWC via press) ....................... PRESS
H2  FFWC bulletin 7 Aug AM: heavy-very heavy rain SE hill basin next 24-48 h ............... PRESS
H3  "Landslide alert issued for Chattogram division" — issuer TBC (BMD by 2026 analogy) ...... PRESS/OPEN
H4  10 killed 8 Aug Bandarban (Kalaghata, Tongkabati, Naikhongchhari, Lama, Thanchi) ....... PRESS
    [SUPERSEDED by R4: 10 deaths from flood and landslides combined]
H5  NAWG #01: Cox's Bazar 5 dead (SHED); 718 homes damaged by landslides; road to Bandarban
    Sadar "snapped due to landslides" .......................................................... SOLID
H6  Bandarban cut off from sub-districts AND from Rangamati (>3 ft water) ................... PRESS
H7  51 deaths total (UNICEF/NAWG) — cause split NOT available ............................. SOLID (no split)

## I. July 2026
I1  Draft Landslide National Early Action Protocol (NEAP): attention/warning/activation
    triggers; BMD issues graded advisories (ICCG SitRep #2, verbatim) ....................... SOLID
I2  BMD Special Warning Bulletin for Landslide No. 05/2026, 7 Jul 13:00; classification at
    UPAZILA and WARD level ("Wards 7, 8, 9 and 14 of CCC") ................................... SOLID
I3  RETRACTED: "district-level, ~8 orders of magnitude" (notes/19). Upazila/ward: ~5-7 orders . RETRACTED
    [5-7 CORRECTED to 4-7 by Y6]
I4  5 Jul forecast -> MoDMR/DDM/BMD/FFWC activated; NDRCC 24/7; district early warning,
    evacuation, shelter (ICCG) ................................................................ SOLID
I5  38,422 in 1,047 shelters (BDRCS SR3); 1,700 shelters activated; ~36,500 displaced ....... SOLID
I6  Rangamati: "comparatively lower risk" 7 Jul -> "upgraded to high... for the first time
    this season" after 287 mm to 8 Jul. Upgrade FOLLOWED the rain ............................. SOLID
I7  Rangamati: 126 landslide incidents (most of any district), 1 death (BDRCS SR3) ........... SOLID
I8  Camps: 8 dead night 6 Jul (3 camps); >=5 students Camp 5 madrasa 8 Jul AFTERNOON;
    UNHCR 15 refugees killed, 4,307 homeless. At HIGH risk, miking, CPP evacuation support .. SOLID
I9  Cox's Bazar host: 5 landslide, 1 wall, 2 drowning of 8 (BDRCS SR3) ..................... SOLID
I10 National toll: GoB 26 (11 Jul) | BDRCS 43 (12 Jul) | media 44 (11 Jul) | UN 59 (22 Jul).
    Always cite source+date ..................................................................... SOLID
I11 Cascade: Bandarban-Ruma/Thanchi blocked; Khagrachari-Rangamati cut at Mahalchhari;
    Baghaichhari/Bilaichhari stranded; Chattogram-Ramgarh under water (BDRCS SR3) ........... SOLID
I12 The Lancet correspondence is health-focused; 0 mentions of warning. Cite for health only .. SOLID

## J. The three-event comparison
J1  Rangamati: 2017 = 146 [now 160, Q2] failures/121 deaths; 2026 = 126 incidents/1 death. Same district,
    comparable forcing (>300 vs 287 mm). Cautions: night-concentrated vs 4-day spread; onset
    timing; incident-count comparability; attribution is inference ........................... SOLID + INFER
J2  Warning layer: none (2017) -> bulletin + alert (2023) -> NEAP + evacuation (2026) ......... SOLID
J3  Residual = EXPOSURE (camps on cut slopes, warned, still buried), not absence/resolution/
    lead time of warning ....................................................................... SOLID + INFER
J4  Night onset in both deep cases (2017; 6 Jul 2026) — but 8 Jul 2026 madrasa was daytime.
    Do NOT claim night onset is THE mechanism; it is one factor ............................. INFER

## K. Competitors / positioning (from the review track — cite, do not fight)
K1  Sarma & Paul 2026 (Mizoram RSF) — same Surma Group; where/how much/WHEN framing ......... SOLID
K2  Sayeem et al. 2026, Adnan et al. 2020 — already make the AUC-inflation argument .......... SOLID
K3  Lucchese & Brenning 2025 — spatial antecedent THRESHOLDS (amount, not timescale) ........ SOLID
K4  "Early-warning systems unfit for compound disasters" (Discover Hazards 2026) — the hook .. SOLID (lit)

## Items still OPEN (in priority order)
1. B6 recompute gauge-density with BWDB's 11 stations included
2. H3 issuer of the 2023 landslide alert  [RESOLVED, R1]
3. G4 when the Chittagong City gauges went live
4. C6 the 14 '13/06/207' records  [RESOLVED, Q1]
5. FFWC flash-flood forecast extension date to SE hills (between 2017 and 2023)
6. Rabby & Li (2018) — the mapping-date methodology (supports C3/C4)

## L. Added while drafting Section 5 (2026-09-22), from BDRCS SitReps 2-3 read verbatim
L1  BDRCS SR3 district table: Cox's Bazar 20 deaths (16 Rohingya), 16 injured (DC office 9-11 Jul);
    camps 15 deaths (UNHCR 10 Jul); Chattogram 5 deaths; Rangamati 1 death, 34 shelters,
    4,265 sheltered vs 3,987 affected; Bandarban deaths not reported ...................... SOLID
L2  Rangamati sheltered > affected (4,265 vs 3,987) -> consistent with precautionary
    evacuation; counts from different sources (NAWG 9 Jul; GoB 9 Jul). Do not read precisely .. INFER
L3  >=21 landslide deaths identifiable 2026: camps 13 (8 on 6 Jul + >=5 Camp 5 madrasa 8 Jul),
    Cox's Bazar host 5, Chattogram 3 (2 children 8 Jul, Rangunia 10 Jul). Matches press 22 ... SOLID
L4  BDRCS SR2 camps at "highest landslide risk": 3, 7, 8E, 8W, 9-14, 16, 18-20, 20Ext.
    Fatal camps 7 and 11 IN the list; 5 and 15 NOT. List date/criteria unstated ............. SOLID (fact) / OPEN (meaning)
L5  Sitakunda UNO confirmed miking in landslide-risk areas before the Jongol Salimpur child death . SOLID
L6  Camp 5 madrasa: 8 Jul AFTERNOON, >=5 students killed, 10 critically injured; after Ukhiya's
    HIGH classification (Bulletin 05, 7 Jul 13:00) ............................................ SOLID
L7  Ukhiya not among units newly upgraded in Bulletin 05 -> implies earlier HIGH; the bulletin in
    force before the 6 Jul deaths not located ................................................. INFER/OPEN

## M. Added while drafting Section 6 (2026-09-22)
M1  H6 correction: the Bandarban approach was under "more than 3 feet" (= 0.9 m), NOT "more than
    a metre". Use 0.9 m ....................................................................... PRESS
M2  2017 Manikchhari: 4 soldiers killed incl. 2 officers, 1 missing (press). District of the
    locality ambiguous in sources (Manikchhari upazila is in Khagrachari; reports say Rangamati).
    Use the locality name only; do not assign a district ...................................... PRESS
M3  2023: NAWG #01 "Road connectivity (communication) and power (electricity) are the most
    impacted areas"; UNICEF "damage of up to 410 kilometres of roads" ........................... SOLID
M4  2026: 241.31 km roads damaged in South Chattogram alone; Chattogram-Cox's Bazar rail line
    suspended near Shomser Para, Kalurghat (BDRCS SR3 citing NAWG 11 Jul); Sapchhari rescue
    after landslide blocked Chattogram-Rangamati highway, 9 Jul (BDRCS SR2) .................... SOLID

## N. Citation corrections from Crossref (2026-09-22) — supersede every earlier note
N1  The Heliyon 2023 LSM review is **Chowdhury, M.S. (2023)**, single author — NOT "Rahman et al."
    as written in notes/01 and outline v1/v2. doi 10.1016/j.heliyon.2023.e17972.
N2  The deployed-threshold chapter (100/200/350 mm) is **Ali, Tunbridge, Bhasin, Akter, Uddin & Khan
    (2018)**, in "Engineering and Mathematical Topics in Rainfall", IntechOpen — NOT Khan & Chang.
N3  ERA5 Bangladesh evaluation = Islam, M.A. & Cartwright, N. (2020), HSJ 65(7):1112-1128.
N4  "The root causes of landslide vulnerability in Bangladesh" = Ahmed, B. (2021), Landslides 18:1707-1720.
N5  Khan et al. antecedent-rainfall paper: Environ Earth Sci 67(1):97-106, print 2012 (online 2011).
N6  Source of the IMERG +18.3 to +92.0% figure is still unconfirmed.

## O. REAL-PRODUCT RERUN (2026-09-22) — SUPERSEDES A3, A5, D2, D3, D4, C4, C5. See notes/22.
O1  ERA5-Land 24 h max 116.3 mm = 0.34 of gauge; IMERG V07 215.5 mm = 0.63. BOTH low ........ SOLID
O2  The opposite-bias bracket premise fails for 2017: IMERG V07 did not overestimate ........ SOLID
O3  Onset 12 Jun 00:00-01:00 in both products = gauge account ............................. SOLID
O4  Gauge-corrected crossings (range over products and 332/343 mm): empirical 24 h 12 Jun
    02:00-08:00 (+16 to +22 h before earliest failures); operational 24 h 12 Jun 19:00-23:00
    (+1 to +5 h); operational 72 h 13 Jun 01:00-05:00 (inside the window); operational 3 h
    crosses under ERA5-Land only (13 Jun 03:00) — not robust .................................. SOLID
O5  Empirical-to-operational 24 h gap = 14-18 h (robust to scaling and product) ............. SOLID
O6  D4 partially reinstated: operational thresholds would have fired 1-5 h before the first
    failures, at night; depends on assumed earliest failure 00:00 ............................. SOLID + INFER
O7  Audit (ERA5-Land): 6 SUSPECT dates / 101 records (22.6%); 2007 disaster SUSPECT (23.9 mm);
    4 dates / 83 records flagged under both proxy and ERA5-Land ............................... SOLID
    [denominator updated by Y1: 101 of 463 = 21.8 %]

## P. Pre-submission check (2026-09-22)
P1  CDMP-II developed a community-based landslide EWS for Cox's Bazar district in 2012 (Ahmed et al.
    2018, IJGI 7:485); a 2010 GoB attempt in Cox's Bazar Municipality "failed due to lack of project
    funding and consequential maintenance" (Ahmed et al. 2020, GNHR 11:446-468) ................. SOLID
P2  "Currently, landslide warnings are given by the Bangladesh Meteorological Department (BMD), and
    are solely based on forecast of heavy rainfall at the regional scale" (Ahmed et al. 2020) .... SOLID
P3  => "No landslide warning in 2017" was TOO STRONG. Correct claim: no DEDICATED landslide warning;
    at most a generic regional heavy-rain caution; no such caution for June 2017 found ......... SOLID
P4  RETRACTED G1 sub-claim: NGO efforts "sporadic... failed" — the quoted wording could not be
    traced to any source in hand. Removed from the text ....................................... RETRACTED
P5  CDMP-II threshold (IJGI 2018): 96 mm in 24 h or 185 mm [duration truncated in extraction] — a
    THIRD threshold set for the region, not yet used in the paper. Consider for §3.4 / §7.3 ..... OPEN
    [RESOLVED by Y2: 185 mm in 48 h]
P6  Camp population: about 1.2 million refugees, most in 33 camps in Cox's Bazar (UN News, Jun 2026) SOLID
P7  Citation fixes: LEWS-lit -> Ahmed et al. 2020 GNHR; CMA-LEWS -> Ahmed et al. 2018 IJGI 7(12):485;
    Roy et al. 2022 pp. 81-94; IMERG-BD removed (uncited; source never confirmed) ............... SOLID
P8  The 100/200/350 mm thresholds belong to the Geological Survey of Bangladesh's four automated
    stations in Chattogram and Cox's Bazar (2015); "the system is not yet functional and publicly
    available, and requires improvements" (Ahmed et al. 2018, IJGI). => call them INSTALLED, not
    operational. Strengthens the institutional argument .................................... SOLID
P9  Bulletin 05/2026 dates of bulletins 01-04 unknown; removed "within two days" ............. RETRACTED
P10 Upazila area "200-500 km2" unverified -> "a few hundred square kilometres" ............... SOFTENED

## Q. Issue-fixing pass (2026-09-23)
Q1  C6 RESOLVED. The 14 records dated "13/06/207" are 13 June 2017, not 2007. All 14 are in
    Rangamati at Manikchhari/Masjid Para/Police Line Sadar; the 2007 cluster is entirely in
    Chittagong district; their centroid lies inside the 13 Jun 2017 cluster; ERA5-Land gives
    116.3 mm/24h there on 13 Jun 2017 against 23.1 mm on 13 Jun 2007. Correction is applied in
    data/scripts/rain_analysis.py (DATE_FIXES) so it is reproducible ......................... SOLID
Q2  Counts revised: 13 Jun 2017 cluster 243 -> **257** (Rangamati 146 -> **160**, Bandarban 91,
    Chittagong 6). Median scar unchanged at 59 m2. Audit now 15 dates covering **460** records.
    Cluster is 3.5x the next largest (was "a factor of three") ................................ SOLID
Q3  Deep-case centroid moves 0.5 km with the 14 added; same ERA5-Land cell, K and all crossing
    times identical. No analysis result changes ............................................... SOLID
Q4  D1 SUPERSEDED. Failure window now rests on published clock times, not on inference from
    "asleep": Bandarban "around 2:30am" and Cox's Bazar "around 3am" on 13 Jun (Dhaka Tribune,
    13 Jun 2017); survivor "just after dawn" (Al Jazeera, 14 Jun 2017); Manikchhari army slide
    "around 11am", four soldiers incl. two officers (Dhaka Tribune; Daily Star) ............... SOLID
Q5  O4/O6 leads recomputed against 02:30: empirical 24 h +18.5 to +24.5 h; installed 24 h
    +3.5 to +7.5 h; installed 72 h -2.5 to +1.5 h (brackets the first failures); installed 3 h
    crosses 03:00 under ERA5-Land only, half an hour AFTER the first failures. Gap between the
    two 24-h thresholds unchanged at 14-18 h ................................................. SOLID
Q6  M2 RESOLVED. Manikchhari is in Rangamati Sadar upazila (Daily Star: "Manikchari, Bedbedi and
    Reserve Bazar areas of Sadar upazila") ................................................... SOLID
Q7  press2017 composite split into DhakaTribune2017, DailyStar2017, AlJazeera2017, each cited for
    the fact it carries. press2023 remains a composite (ReliefWeb blocked) ................. PART DONE

## R. August 2023 moved to primary sources (2026-09-23)
Sources now in corpus/pdf: BDRCS "Flash Flood and Landslide in Chattogram Region" SitRep 1
(7 Aug 2023) and SitRep 2 (16 Aug 2023); ECHO Daily Flash 10 Aug 2023. press2023 retired; no press
composite remains anywhere in the manuscript.
R1  H3 RESOLVED. The landslide alert was issued by the METEOROLOGICAL DEPARTMENT: BMD "issued a
    severe to extremely severe rainfall warning for six districts" and "also issued a landslide
    alert for the Chattogram division because of potential heavy rain" (BDRCS SitRep 1) ....... SOLID
R2  H2 verbatim confirmed: FFWC daily bulletin, morning of 7 Aug, "a chance of heavy to very heavy
    rainfall in the South-eastern hill basin & adjacent upstream parts of Bangladesh in next
    24-48 hours" ............................................................................. SOLID
R3  H1 confirmed and extended: Matamuhuri +199 cm at Lama on 6 Aug afternoon (flood begins);
    Sangu +283 cm on 7 Aug. Chattogram recorded 322 mm in 24 h to 8:00 on 6 Aug (BMD) ......... SOLID
R4  H4 CORRECTED. "Ten people were killed in landslides" was WRONG. BDRCS SitRep 2: "10 deaths
    have been reported resulting from the flood and landslides" — combined, not separated ..... SOLID
R5  NEW, and it changes the arc: 2023 DID act on warning. "More than 200 BDRCS volunteers ...
    disseminated Early Warning Messages (EWM) and helped people in safe evacuation from the
    high-risk prone landslide areas in Bandarban and Chattogram"; ~33,000 in 208 temporary
    shelters, 234 more opened by district administration (SitRep 2); >50,000 in 1,348 flood
    shelters by 10 Aug, >1 million affected (ECHO) ........................................... SOLID
    => Table 1 "Action on warning: Not documented" for 2023 was wrong and is replaced. The step
       from 2023 to 2026 is smaller than the paper implied: evacuation existed in 2023; what 2026
       added is upazila/ward-level bulletins and the tiered protocol.
R6  H6 now primary: "Bandarban city was cut off from most of its sub-districts and Rangamati hill
    district due to impassable roads, including the key entry route from Chattogram, submerged
    under more than 3 feet of water" (SitRep 2); named damaged roads from SitRep 1 ............ SOLID
R7  BDRCS hosts no Aug-2023 flood situation reports on its own server (WordPress media listing
    shows only Cyclone Mocha, dengue and Cyclone Hamoon for 2023); the two SitReps came from the
    user .................................................................................... NOTE

## S. Full read-through of the compiled PDF (2026-09-23)
S1  §7.6 said the 2017 failure window was "eleven-hour" while §3.3 said nine hours after the
    clock-time revision. Corrected to nine ......................................... CONTRADICTION FIXED
S2  §2.4 source list for 2023 named only NAWG and UNICEF; BDRCS SitReps 1-2 and ECHO, which §4.2
    and §6 now rely on, were missing. Added ................................................. FIXED
S3  Figure 2 still showed the pre-BDRCS 2023 lane: "10 killed, Bandarban" (wrong, the 10 are flood
    and landslide together) and no action mark. Now "10 deaths, flood and landslides" plus
    "33,000 sheltered" ...................................................................... FIXED
S4  ECHO citation printed the full 12-word organisation name; bib author shortened to DG ECHO .. FIXED
S5  §4.2 "blocked the Rangamati ... roads" was ambiguous; the source says Bandarban-Rangamati .. FIXED
S6  §4.3 said the advisory/activation split was "the step that neither the 2017 nor the 2023
    arrangements contained", which now contradicts §4.2's evacuation evidence. Changed to
    "formalised, although 2023 acted on its alert without one" ............................... FIXED
S7  §3.5 called CDMP-II "the only documented dedicated effort", ignoring the GSB automated
    stations of §3.4. Now "Two dedicated efforts are documented, and neither was running" ..... FIXED
S8  §7.3 repeated "the two most recent threshold sets" in consecutive sentences ............... FIXED
S9  Figure 2: the 2017 "no dedicated warning" caption overlapped the lane label; shifted ....... FIXED
Read-through also confirmed: no stale counts (257/160/460), no press composites, abstract 150 w,
0 undefined references, all \reg IDs resolve, three TODOs remain (affiliation, email, repo URL).

## W. Rainfall climatology 1950-2025 (2026-09-26)
Source for all: data/results/climatology.json and climatology_annual_maxima.csv, from
data/scripts/climatology.py on ERA5-Land hourly May-Oct 1950-2026 (77 files, each verified at
4,416 h; 2026 = 3,443 h to 21 Sep 10:00 UTC). Uncorrected ERA5-Land; ranks only.
W1  2026 season incomplete (ends 21 Sep); excluded from MK, Sen, GEV and threshold-day trends .. SOLID
W2  Annual max 24h, 1950-2025 (n=76): Rangamati MK Z=-1.20 p=0.23 Sen -2.6 %/dec;
    Bandarban Z=-0.29 p=0.77 Sen -0.6 %/dec. No significant trend ............................ SOLID
W3  Step at 1979: median annual max 24h 1950-78 vs 1979-2025 = 111 vs 92 mm (Rangamati, +21 %),
    123 vs 99 mm (Bandarban, +24 %). Coincides with satellite era (Bell et al. 2021). That the
    step is a reanalysis artefact is INFERENCE, not shown ...................................... INFER
W4  1979-2025 (n=47): 24h Rangamati Z=+1.63 p=0.10 Sen +7.0 %/dec; Bandarban Z=+1.63 p=0.10
    +6.9 %/dec. 72h Rangamati p=0.21 (+6.1 %/dec), Bandarban p=0.095 (+5.5 %/dec) ............. SOLID
W5  Threshold-day counts (thresholds / 2.95): 1979-2025 p = 0.21 (R, 57.4), 0.063 (B, 57.4),
    0.47 (R, 200), 0.66 (B, 200). Full record: R 200-mm days decline p=0.039, gone from 1979.
    Absolute counts (~40 d/season at 57.4) are implausible: the single-event factor over-corrects
    ordinary rain. Use counts for TREND ONLY, never quote a days-per-season figure ............. SOLID
W6  Event-year season maxima (24h, GEV on 1950-2025): 2017 = 116.3 mm R / 120.8 mm B, RP 2.6 y
    at both; 2023 RP 1.6 / 1.2 y; 2026-to-date RP 2.1 / 1.7 y. These are SEASON maxima, an upper
    bound on the event: Rangamati 2023 max fell 27 Aug (event 8-9 Aug); Bandarban 2017 72h max
    fell 25 Jul. ERA5-Land cannot rank the events; do not quote these as event return periods .. SOLID

## Y. Consistency pass (2026-09-26) — full read against register, data and figures
Y1  Three records dated '15/06/217' (Rangunia Eco Park, Chattogram) read as 15/06/2017: 15 km
    from the Rangunia/Gomra records already on that date; '217' admits no other reading in
    2001-2017. Added to DATE_FIXES in rain_analysis.py; audit rerun. 15/06/2017 now 25 records
    (OK, 107.1 mm); audit 15 dates / 463 records; SUSPECT unchanged at 6 dates / 101 records
    (21.8 %); nearest-cell offset now up to 7.1 km. 13 Jun cluster and all crossings unchanged  SOLID
Y2  P5 resolved: CDMP-II threshold is 96 mm in 24 h or 185 mm in 48 h; "no longer active, as no
    follow-up activities or long-term maintenance" (Ahmed et al. 2018, IJGI, verified in PDF) .. SOLID
Y3  Sangu at Bandarban 2026: 15.76 m = +96 cm DL (MSL datum), 8 Jul (Daily Star, 8 Jul 2026) .. PRESS
Y4  2017 deaths: Rangamati 121; national 150-170 by source and date (Dhaka Tribune; Daily Star).
    First published failure time (02:30) is at BANDARBAN; Rangamati's first is "just after dawn",
    so lead times at the Rangamati centroid measured to 02:30 are LOWER BOUNDS ............... PRESS / INFER
Y5  ERA5 underestimates Bangladesh rainfall above the 75th percentile by up to 85 % (Islam &
    Cartwright 2020, N3; notes/11) ........................................................... SOLID (lit)
Y6  Advisory unit vs 59 m2 median scar: upazila (few hundred km2) ~6.5-7 orders; city ward
    (~1-5 km2) ~4-5 orders. Quote "four to seven" ........................................... SOLID (arith)
Y7  Empirical 72 h (130 mm) gauge-corrected crossings: 12 Jun 03:00-11:00, 1-3 h after the
    empirical 24 h crossing (june2017_crossings.json) ....................................... SOLID
Y8  Anchor caveat: the 332/343 mm gauge peak is at Bandarban (~45 km S of the Rangamati centroid);
    no Rangamati gauge value is published. Stated in §2.3 and §7.6 ........................... INFER
Y9  A7 clarified: 856 mm at Bandarban is the MONTHLY total to 10 Aug 2023, not 5-10 Aug.
    With R3 (322 mm/24 h at Chattogram, 6 Aug) 2023 is "sustained", not "moderate" ........... SOLID
Y10 2023 FFWC bulletin (R2) is a RAINFALL outlook; whether a formal flash flood forecast covered
    the SE hills in 2023 remains OPEN (open item 5) ......................................... OPEN
Y11 Data availability now cites the CONCEPT DOI 10.5281/zenodo.22917014; the version DOI
    22917015 is v1.0.0, which lacks the climatology and has the broken figure script ......... NOTE
Y12 Figure 2's July 2026 panel extended to 18 Jul (rain 14-18 Jul at Bandarban 1.5-7.8 mm/day)
    from the climatology season file, identical to the event file to 4e-6 mm over 3-13 Jul ..... SOLID

