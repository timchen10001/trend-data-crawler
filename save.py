from merge import merge_day, merge_week

def save(
    daily: bool,
    cross_year: bool,
    columns_name: str
):
    merge_week(sequence_type='none-cross', new_folder='merged', cn=columns_name)
    if cross_year:
        merge_week(sequence_type='cross-year', new_folder='merged', cn=columns_name)
    if daily:
        merge_day(new_folder='merged', table_type='single-column',
                  sequence_type='none-cross', cn=columns_name)