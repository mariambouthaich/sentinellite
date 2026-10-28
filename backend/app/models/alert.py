class Rule(Base):          # table "rules"
    code            # "R1", "R2"...
    name, description
    enabled         # règle activée ou non
    threshold_config  # seuils en JSON (ex: 5 échecs en 3 min)

class Alert(Base):         # table "alerts"
    rule_id         # quelle règle l'a déclenchée
    severity        # low | medium | high
    reason          # explication lisible
    status          # open | in_progress | resolved
    created_at

class AlertEvent(Base):    # table "alert_events"
    alert_id, event_id   # clé composite