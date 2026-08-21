import sys

file_path = "alembic/versions/2026_08_20_1457-f708a51d6e58_add_userprofile_achievements_and_.py"
with open(file_path, "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "op.drop_index(op.f('ix_sample_items_id')" in line: continue
    if "op.drop_table('sample_items')" in line: continue
    if "op.create_table('sample_items'" in line:
        skip = True
        continue
    if skip and line.strip() == ")":
        skip = False
        continue
    if skip: continue
    if "op.create_index(op.f('ix_sample_items_id')" in line: continue
    
    new_lines.append(line)

with open(file_path, "w") as f:
    f.writelines(new_lines)
