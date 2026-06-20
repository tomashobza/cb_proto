import enum


class OrgRole(enum.Enum):
  INTERN = "Intern"
  ASSOCIATE = "Associate"
  SENIOR_ASSOCIATE = "Senior Associate"
  MANAGER = "Manager"
  DIRECTOR = "Director"
  VP = "VP"
  C_SUITE = "C-Suite"


ORG_PROGRESSION = (
  OrgRole.INTERN,
  OrgRole.ASSOCIATE,
  OrgRole.SENIOR_ASSOCIATE,
  OrgRole.MANAGER,
  OrgRole.DIRECTOR,
  OrgRole.VP,
  OrgRole.C_SUITE,
)

ROLE_LEVELS = {
  role: index
  for index, role in enumerate(ORG_PROGRESSION)
}


def _normalize_key(value):
  return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def normalize_role(role):
  if isinstance(role, OrgRole):
    return role
  if isinstance(role, str):
    role_key = _normalize_key(role)
    for org_role in OrgRole:
      if role_key in {_normalize_key(org_role.name), _normalize_key(org_role.value)}:
        return org_role
  raise ValueError(f"Unknown org role: {role}")


def normalize_level(value):
  if isinstance(value, int):
    if 0 <= value < len(ORG_PROGRESSION):
      return value
    raise ValueError(f"Org level must be between 0 and {len(ORG_PROGRESSION) - 1}")
  return role_level(value)


def role_level(role):
  return ROLE_LEVELS[normalize_role(role)]


def next_role(role):
  role = normalize_role(role)
  index = ROLE_LEVELS[role]
  if index + 1 >= len(ORG_PROGRESSION):
    return None
  return ORG_PROGRESSION[index + 1]


def is_senior_to(left, right):
  return role_level(left) > role_level(right)


def is_junior_to(left, right):
  return role_level(left) < role_level(right)
