# Comparaison des 3 Analyseurs NLP Coréens
## Analyse Complète de 1,021 Discours de Lee Seung Man (이승만)

---

## ⏱️ PERFORMANCES - Temps d'Exécution

| Analyseur | Temps Total | Vitesse | Noms Extraits | Noms Uniques |
|-----------|-------------|---------|---------------|--------------|
| **Komoran** ⚡ | **24.56 s** | **41.6 disc/s** | 183,526 | 10,163 |
| **Hannanum** | 60.43 s | 16.9 disc/s | 184,828 | 36,557 |
| **Kkma** 🐌 | 237.97 s | 4.3 disc/s | 145,205 | 23,369 |

### 📈 Ratio de Vitesse
- Komoran est **9.7x plus rapide** que Kkma
- Komoran est **2.5x plus rapide** que Hannanum
- Hannanum est **3.9x plus rapide** que Kkma

---

## 🏆 TOP 10 MOTS LES PLUS FRÉQUENTS - Comparaison

| Rang | **Komoran** | Fréq. | **Hannanum** | Fréq. | **Kkma** | Fréq. |
|------|-------------|-------|--------------|-------|----------|-------|
| **1** | 사람 (personne) | 4,267 | 사람 (personne) | 3,432 | 대통령 (président) | 933 |
| **2** | 정부 (gouvernement) | 2,336 | 정부 (gouvernement) | 1,629 | 사람 (personne) | 737 |
| **3** | 나라 (pays) | 1,792 | 우리나라 (notre pays) | 1,179 | 나라 (pays) | 665 |
| **4** | 대통령 (président) | 1,606 | 나라 (pays) | 1,138 | 정부 (gouvernement) | 599 |
| **5** | 세계 (monde) | 1,509 | 생각 (pensée) | 1,069 | 생각 (pensée) | 522 |
| **6** | 한국 (Corée) | 1,370 | 세계 (monde) | 1,069 | 자기 (soi-même) | 486 |
| **7** | 미국 (États-Unis) | 1,337 | 미국 (États-Unis) | 938 | 우리나라 (notre pays) | 463 |
| **8** | 자유 (liberté) | 1,313 | 한국 (Corée) | 862 | 국가 (État) | 445 |
| **9** | 국가 (État) | 1,266 | 자유 (liberté) | 758 | 세계 (monde) | 432 |
| **10** | 생각 (pensée) | 1,246 | 문제 (problème) | 611 | 자유 (liberté) | 401 |

---

## 📊 ANALYSE THÉMATIQUE

### Mots Communs dans les 3 Top 10

| Mot | Komoran | Hannanum | Kkma | Thème |
|-----|---------|----------|------|-------|
| **사람** (personne) | #1 (4,267) | #1 (3,432) | #2 (737) | 👥 Peuple |
| **정부** (gouvernement) | #2 (2,336) | #2 (1,629) | #4 (599) | 🏛️ Politique |
| **나라** (pays) | #3 (1,792) | #4 (1,138) | #3 (665) | 🇰🇷 Nation |
| **세계** (monde) | #5 (1,509) | #6 (1,069) | #9 (432) | 🌍 International |
| **자유** (liberté) | #8 (1,313) | #9 (758) | #10 (401) | 🗽 Idéologie |
| **생각** (pensée) | #10 (1,246) | #5 (1,069) | #5 (522) | 💭 Réflexion |

### Mots Spécifiques par Analyseur

**Komoran uniquement :**
- 대통령 (président) - #4
- 한국 (Corée) - #6
- 미국 (États-Unis) - #7
- 국가 (État) - #9

**Hannanum uniquement :**
- 우리나라 (notre pays) - #3
- 미국 (États-Unis) - #7
- 한국 (Corée) - #8
- 문제 (problème) - #10

**Kkma uniquement :**
- 대통령 (président) - #1
- 자기 (soi-même) - #6
- 우리나라 (notre pays) - #7
- 국가 (État) - #8

---

## 🎯 THÈMES PRINCIPAUX IDENTIFIÉS

### 1. **Gouvernance & Politique** 🏛️
- 정부 (gouvernement)
- 대통령 (président)
- 국가 (État)
- 국회 (Assemblée nationale)

### 2. **Identité Nationale** 🇰🇷
- 나라 (pays)
- 한국 (Corée)
- 우리나라 (notre pays)
- 민족 (nation/peuple)

### 3. **Relations Internationales** 🌍
- 미국 (États-Unis)
- 세계 (monde)
- 일본 (Japon)

### 4. **Idéologie & Valeurs** 🗽
- 자유 (liberté)
- 민주 (démocratie)
- 평화 (paix)

### 5. **Peuple & Société** 👥
- 사람 (personne)
- 동포 (compatriotes)
- 민중 (peuple)

---

## 💡 RECOMMANDATIONS PAR CAS D'USAGE

### Pour l'Analyse de Contenu Politique ✓
→ **KOMORAN**
- ✅ Le plus rapide (24.56s)
- ✅ Meilleur équilibre fréquence/pertinence
- ✅ Identifie clairement les concepts clés

### Pour l'Analyse Linguistique Approfondie
→ **KKMA**
- ✅ Analyse morphologique la plus détaillée
- ✅ Segmentation en phrases
- ⚠️ Très lent (237.97s = 4 minutes)

### Pour un Compromis Vitesse/Qualité
→ **HANNANUM**
- ✅ Vitesse acceptable (60.43s)
- ✅ Résultats cohérents
- ⚠️ Tags POS moins précis

---

## 📈 STATISTIQUES DÉTAILLÉES

### Extraction de Noms

| Métrique | Komoran | Hannanum | Kkma |
|----------|---------|----------|------|
| **Total noms** | 183,526 | 184,828 | 145,205 |
| **Noms uniques** | 10,163 | 36,557 | 23,369 |
| **Moyenne/discours** | 179.8 | 181.0 | 142.2 |
| **Ratio unique/total** | 5.5% | 19.8% | 16.1% |

**Observation** : Komoran normalise mieux (moins de variantes), d'où moins de noms uniques.

---

## 🏁 CONCLUSION

### 🥇 Gagnant Global : **KOMORAN**

**Pour l'analyse de 1,021 discours présidentiels :**
1. ⚡ **Vitesse exceptionnelle** : 24.56s vs 237.97s (Kkma)
2. 🎯 **Meilleur top 10** : Concepts politiques clairs et pertinents
3. 📊 **Extraction efficace** : 183,526 noms avec bonne normalisation
4. 💰 **Meilleur rapport qualité/vitesse**

**Consensus des 3 analyseurs :**
Les discours de Lee Seung Man se concentrent sur :
- Le **gouvernement** et la **politique**
- La **liberté** et la **démocratie**
- Les relations avec les **États-Unis** et le **monde**
- L'identité **nationale** coréenne
- Le **peuple** et la **société**

---

## 📁 Fichiers de Résultats

- `lee_seung_man_nlp_analysis.json` - Komoran
- `lee_seung_man_all_analyzers.json` - Comparaison complète
- `kkma_no_metadata_analysis.json` - Kkma sans métadonnées
