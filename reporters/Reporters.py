from datetime import datetime

import pandas as pd

from config.Settings import (
    CSV_FILENAME,
    OUTPUT_DIR,
    REPORT_FILENAME,
    CONSISTENCY_REPORT_FILENAME,
    GLAUCOMA_AREA_CDR_THRESHOLD,
)
from readers.Readers import PairingResult


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
                    f"  Sinalizados: {df['area_cdr_flag'].sum()} / {len(df)}",
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
            flag = "⚠️" if row["area_cdr_flag"] else "  "
            lines.append(
                f"  {flag} {row['image_id']:<20} | "
                f"Disco: {int(row['disc_pixels']):>8,} | "
                f"Copo: {int(row['cup_pixels']):>8,} | "
                f"Area CDR: {row['area_cdr']:.4f}"
            )

        lines += ["", sep]

        dest.write_text("\n".join(lines), encoding="utf-8")

        print(f"  [TXT] Salvo em: {dest}")


class ConsistencyReporter:

    def save(self, result: PairingResult) -> None:
        dest = OUTPUT_DIR / CONSISTENCY_REPORT_FILENAME
        dest.parent.mkdir(parents=True, exist_ok=True)

        sep = "=" * 60
        lines = [
            sep,
            "  RELATÓRIO — Consistência do Dataset (disco x copo)",
            f"  Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep,

            "",
            "RESUMO",
            f"  Pares válidos          : {len(result.pairs)}",
            f"  Discos sem copo        : {len(result.missing_cup)}",
            f"  Copos sem disco        : {len(result.missing_disc)}",
            f"  Nomes duplicados (disco): {len(result.duplicated_disc)}",
            f"  Nomes duplicados (copo) : {len(result.duplicated_cup)}",
        ]

        self._add_section(lines, "DISCOS SEM COPO CORRESPONDENTE", result.missing_cup)
        self._add_section(lines, "COPOS SEM DISCO CORRESPONDENTE", result.missing_disc)
        self._add_section(lines, "NOMES DUPLICADOS NA PASTA DE DISCO", result.duplicated_disc)
        self._add_section(lines, "NOMES DUPLICADOS NA PASTA DE COPO", result.duplicated_cup)

        lines += ["", sep]

        dest.write_text("\n".join(lines), encoding="utf-8")

        print(f"  [TXT] Salvo em: {dest}")

    @staticmethod
    def _add_section(lines: list[str], title: str, items: list[str]) -> None:
        lines.append("")
        lines.append(title)
        if items:
            lines.extend(f"  - {item}" for item in items)
        else:
            lines.append("  (nenhum)")