import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { InsightList } from "./InsightList";

type Props = {
  id: string;
  index: number;
  label: string;
  claim: ReactNode;
  lead: string;
  close?: string;
  insights?: string[];
  children: ReactNode;
};

export function ActShell({
  id,
  index,
  label,
  claim,
  lead,
  close,
  insights,
  children,
}: Props) {
  return (
    <section className="act" id={id} data-act={index}>
      <div className="act-frame">
        <div className="copy">
          <motion.div
            className="act-kicker"
            initial={{ y: 8 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.4 }}
          >
            <span className="bar" />
            <span>
              Act {String(index).padStart(2, "0")} · {label}
            </span>
          </motion.div>

          <motion.h2
            className="act-claim"
            initial={{ y: 12 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.5, delay: 0.03 }}
          >
            {claim}
          </motion.h2>

          <motion.p
            className="act-lead"
            initial={{ y: 10 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.4, delay: 0.06 }}
          >
            {lead}
          </motion.p>

          {close ? <p className="act-close">{close}</p> : null}

          <InsightList items={insights || []} max={2} compact />
        </div>

        <motion.div
          className="act-stage"
          initial={{ y: 14 }}
          whileInView={{ y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.5, delay: 0.05 }}
        >
          {children}
        </motion.div>
      </div>
    </section>
  );
}
