new_css = """

/* ── Split Layout for Module Pages (Radar, Terrain, Fusion, Rover) ── */
.split-sec {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
  min-height: 80vh;
  padding: 40px;
}
.split-sec.rev {
  flex-direction: row-reverse;
}
.split-content {
  flex: 1;
  max-width: 500px;
}
.split-visual {
  flex: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}
@media (max-width: 900px) {
  .split-sec {
    flex-direction: column;
  }
  .split-sec.rev {
    flex-direction: column;
  }
}

/* ── Content Descriptions ── */
.c-desc {
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.8;
  color: rgba(255,255,255,0.6);
  margin-bottom: 40px;
}

/* ── Telemetry Stats (.r-stats) ── */
.r-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}
.r-metric {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.r-lbl {
  font-family: var(--font-mono);
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}
.r-val {
  font-family: var(--font-h);
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
}
.r-bar {
  width: 100%;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 12px;
}
.r-fill {
  height: 100%;
  width: 0%;
  border-radius: 2px;
  transition: width 1.5s cubic-bezier(0.22, 1, 0.36, 1);
}
.r-tag {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* Specific colors for metrics */
.m-cpr .r-fill { background: var(--ice); box-shadow: 0 0 10px var(--ice); }
.m-cpr .r-val, .m-cpr .r-tag { color: var(--ice); }
.m-cpr { border-left: 3px solid var(--ice); }

.m-dop .r-fill { background: var(--green); box-shadow: 0 0 10px var(--green); }
.m-dop .r-val, .m-dop .r-tag { color: var(--green); }
.m-dop { border-left: 3px solid var(--green); }

.m-ice .r-fill { background: var(--isro); box-shadow: 0 0 10px var(--isro); }
.m-ice .r-val, .m-ice .r-tag { color: var(--isro); }
.m-ice { border-left: 3px solid var(--isro); }

.m-dep .r-fill { background: var(--gold); box-shadow: 0 0 10px var(--gold); }
.m-dep .r-val, .m-dep .r-tag { color: var(--gold); }
.m-dep { border-left: 3px solid var(--gold); }

/* ── Algorithm Lists (.algo-list) ── */
.algo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.algo-li {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.ali-n {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.2);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  color: rgba(255,255,255,0.8);
}
.ali-t {
  font-family: var(--font-h);
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}
.ali-d {
  font-family: var(--font-mono);
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  line-height: 1.6;
}

/* ── Visual Overlays (.vis-overlay, .vis-canvas) ── */
.vis-overlay {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  gap: 10px;
  z-index: 10;
}
.vis-tag {
  padding: 6px 12px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.1em;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
}
.v-r { color: #FF3366; border-color: rgba(255,51,102,0.3); }
.v-i { color: var(--ice); border-color: rgba(79,195,247,0.3); }

.vis-canvas {
  width: 100%;
  max-width: 600px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.05);
  box-shadow: 0 0 80px rgba(79,195,247,0.05), inset 0 0 40px rgba(0,0,0,0.8);
  background: radial-gradient(circle, rgba(255,255,255,0.02) 0%, transparent 70%);
}
"""

with open('style.css', 'a') as f:
    f.write(new_css)
