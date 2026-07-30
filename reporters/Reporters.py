from datetime import datetime
from pathlib import Path

import pandas as pd

from config.Settings import CSV_FILENAME, OUTPUT_DIR, REPORT_FILENAME, GLAUCOMA_DISCREPANCY_THRESHOLD_PCT


class CsvReporter:

    def save(self, df: pd.DataFrame) -> None:
        dest = OUTPUT_DIR / CSV_FILENAME
        dest.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(dest, index=False)
        print(f"  [CSV] Salvo em: {dest}")


class TxtReporter:

    def save(self, df: pd.DataFrame) -> None:
        dest = OUTPUT_DIR / REPORT_FILENAME
        dest.parent.mkdir(parents=True, exist_ok=True)

        r = df["ratio_cup_disc"]
        d = df["discrepancy_pct"]
        sep = "=" * 60

        lines = [
            sep,
            "  RELATÓRIO — Discrepância Copa Óptica vs Disco Óptico",
            f"  Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep,

            "",
            "RESUMO",
            f"  Imagens analisadas : {len(df)}",
            f"  Critério           : pixels não-pretos (qualquer canal > 0)",

            "",
            "RAZÃO (Copa Óptica / Disco Óptico)",
            f"  Média   : {r.mean():.4f}",
            f"  Mediana : {r.median():.4f}",
            f"  Desvio  : {r.std():.4f}",
            f"  Min     : {r.min():.4f}",
            f"  Max     : {r.max():.4f}",

            "",
            "DISCREPÂNCIA (%)",
            f"  Média   : {d.mean():.2f}%",
            f"  Mediana : {d.median():.2f}%",
            f"  Desvio  : {d.std():.2f}%",
            f"  Min     : {d.min():.2f}%",
            f"  Max     : {d.max():.2f}%",

            "",
            "PREDOMINÂNCIA",
            *[f"  {label:<10}: {n} imagens ({n / len(df) * 100:.1f}%)"
              for label, n in df["predominance"].value_counts().items()],

            "",
            "GLAUCOMA FLAG",
            *([f"  Threshold : {GLAUCOMA_DISCREPANCY_THRESHOLD_PCT:.1f}%",
               f"  Flagados  : {df['glaucoma_flag'].sum()} / {len(df)}"]
              if GLAUCOMA_DISCREPANCY_THRESHOLD_PCT
              else ["  Threshold : não definido (ver config/settings.py)"]),

            "",
            "TOP 10 MAIORES DISCREPÂNCIAS",
            "-" * 60,
        ]

        for _, row in df.nlargest(10, "discrepancy_pct").iterrows():
            flag = "⚠" if row["glaucoma_flag"] else " "
            lines.append(
                f"  {flag} {row['image_id']:<6} | "
                f"Disco Óptico: {int(row['disc_pixels']):>8,} | "
                f"Copa Óptica: {int(row['cup_pixels']):>8,} | "
                f"Disc: {row['discrepancy_pct']:>5.1f}%"
            )

        lines += ["", sep]

        dest.write_text("\n".join(lines), encoding="utf-8")
        print(f"  [TXT] Salvo em: {dest}")