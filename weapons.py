# ==============================================================================
# MÓDULO: REPOSITORIO DE COMPOSICIÓN DE ARMAMENTO
# ==============================================================================

class WeaponProfile:
    def __init__(self, name, damage, radius, speed_mult, cost, desc, special_type="normal"):
        self.name = name
        self.damage = damage       
        self.radius = radius       
        self.speed_mult = speed_mult
        self.cost = cost
        self.desc = desc
        self.special_type = special_type  

CHARACTER_WEAPONS = {
    'Knight': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Missile Táctico", damage=46, radius=38, speed_mult=1.05, cost=35, desc="Misil perforador azul."),
        WeaponProfile("Double Shot", damage=25, radius=24, speed_mult=1.0, cost=65, desc="Lanza 2 misiles de impacto continuo.", special_type="double"),
        WeaponProfile("Shield Strike", damage=50, radius=32, speed_mult=1.18, cost=75, desc="Impacto cinético lineal rápido."),
        WeaponProfile("Holy Bomb", damage=68, radius=58, speed_mult=0.9, cost=130, desc="Explosión bendita masiva.")
    ],
    'Mage': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Fireball Plasma", damage=52, radius=52, speed_mult=0.95, cost=50, desc="Onda ígnea expansiva."),
        WeaponProfile("Thunder Strike", damage=55, radius=36, speed_mult=1.1, cost=80, desc="Rayo electromagnético vertical.", special_type="thunder"),
        WeaponProfile("Magic Arrow", damage=38, radius=20, speed_mult=1.45, cost=45, desc="Saeta de plasma veloz."),
        WeaponProfile("Meteor Inbound", damage=76, radius=65, speed_mult=0.85, cost=140, desc="Meteoro denso de alta destrucción.")
    ],
    'Dragon': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Poison Shot", damage=44, radius=34, speed_mult=1.1, cost=40, desc="Plasma ácido corrosivo."),
        WeaponProfile("Flame Breath", damage=48, radius=46, speed_mult=1.0, cost=55, desc="Fuego místico molecular."),
        WeaponProfile("Dragon Fang", damage=56, radius=38, speed_mult=1.22, cost=85, desc="Perforador colmillar pesado."),
        WeaponProfile("Earthquake", damage=62, radius=68, speed_mult=0.88, cost=120, desc="Onda sismológica destructora.")
    ],
    'Heavy': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Atomic Bomb", damage=92, radius=92, speed_mult=0.7, cost=200, desc="Ojiva de destrucción masiva."),
        WeaponProfile("Big Missile", damage=58, radius=48, speed_mult=0.92, cost=70, desc="Fragmentación pesada."),
        WeaponProfile("Machine Gun", damage=18, radius=20, speed_mult=1.28, cost=60, desc="Ráfaga continua de 3 disparos.", special_type="machinegun"),
        WeaponProfile("Bunker Buster", damage=48, radius=42, speed_mult=1.12, cost=90, desc="Taladra antes de estallar.", special_type="buster")
    ]
}