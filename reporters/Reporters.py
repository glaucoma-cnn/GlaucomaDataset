from datetime import datetime

import pandas as pd

from config.Settings import (
    CSV_FILENAME,
    OUTPUT_DIR,
    REPORT_FILENAME,
    GLAUCOMA_AREA_CDR_THRESHOLD,
)


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

        cdr = df["area_cdr"]
        d = df["discrepancy_pct"]

        sep = "=" * 60

        lines = [
            sep,
            "  RELATÓRIO — Análise do Disco Óptico e Copo Óptico",
            f"  Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep,

            "",
            "RESUMO",
            f"  Imagens analisadas : {len(df)}",
            "  Critério das máscaras: pixels não-pretos (qualquer canal > 0)",

            "",
            "AREA CDR (Área do Copo / Área do Disco)",
            f"  Média   : {cdr.mean():.4f}",
            f"  Mediana : {cdr.median():.4f}",
            f"  Desvio  : {cdr.std():.4f}",
            f"  Min     : {cdr.min():.4f}",
            f"  Max     : {cdr.max():.4f}",

            "",
            "DISCREPÂNCIA (%)",
            f"  Média   : {d.mean():.2f}%",
            f"  Mediana : {d.median():.2f}%",
            f"  Desvio  : {d.std():.2f}%",
            f"  Min     : {d.min():.2f}%",
            f"  Max     : {d.max():.2f}%",

            "",
            "CONSISTÊNCIA ANATÔMICA",
            (
                f"  Consistentes : "
                f"{df['anatomical_consistency'].sum()} / {len(df)}"
            ),
            (
                f"  Inconsistentes: "
                f"{(~df['anatomical_consistency']).sum()} / {len(df)}"
            ),

            "",
            "TRIAGEM POR AREA CDR",
            *(
                [
                    f"  Threshold : {GLAUCOMA_AREA_CDR_THRESHOLD:.4f}",
                    f"  Sinalizados: {df['glaucoma_flag'].sum()} / {len(df)}",
                    "  Observação: sinalização preliminar; não representa diagnóstico.",
                ]
                if GLAUCOMA_AREA_CDR_THRESHOLD is not None
                else [
                    "  Threshold : não definido (ver config/Settings.py)"
                ]
            ),

            "",
            "TOP 10 MAIORES AREA CDR",
            "-" * 60,
        ]

        for _, row in df.nlargest(10, "area_cdr").iterrows():
            flag = "⚠" if row["glaucoma_flag"] else " "

            lines.append(
                f"  {flag} {row['image_id']:<20} | "
                f"Disco: {int(row['disc_pixels']):>8,} | "
                f"Copo: {int(row['cup_pixels']):>8,} | "
                f"Area CDR: {row['area_cdr']:.4f}"
            )

        lines += ["", sep]

        dest.write_text("\n".join(lines), encoding="utf-8")

        print(f"  [TXT] Salvo em: {dest}")