from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, update_saved
from app.db.models import Label, CustomField, Story, StoryCustomFields, CustomFieldValue
from app.db.schemas import CustomFieldBase, LabelBase, StoryBase
from app.resources.resources import resources

router = APIRouter(prefix='/admin/shortcut', tags=['shortcut', 'admin'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/labels', response_model=List[LabelBase])
async def get_labels_from_shortcut(db: Session = Depends(get_db)):
    labels = await resources.shortcut.get_labels()
    db_labels = [
        Label(id=label['id'],
              name=label['name'])
        for label in labels
    ]

    db_labels = await update_saved(db, Label, db_labels)
    return db_labels


@router.get('/fields', response_model=List[CustomFieldBase])
async def get_custom_fields_from_shortcut(db: Session = Depends(get_db)):
    fields = await resources.shortcut.get_fields()
    db_fields = []
    for field in fields:
        field_values = [
            CustomFieldValue(field_id=field['id'],
                             value_id=value['id'],
                             value=value['value'])
            for value in field['values']
        ]
        db_fields.append(CustomField(id=field['id'],
                                     name=field['name'],
                                     field_values=field_values))

    db_fields = await update_saved(db, CustomField, db_fields)
    return db_fields


@router.get('/backlog')
async def get_backlog_from_shortcut(db: Session = Depends(get_db)):
    labels = {label.id: label
              for label in await get_labels_from_shortcut(db)}
    stories = await resources.shortcut.get_stories(state='Önskemål', limit=-1)
    db_stories = [
        Story(id=story['id'],
              name=story['name'],
              shortcut_url=story['app_url'],
              custom_fields=[StoryCustomFields(
                  story_id=story['id'],
                  custom_field_value_id=field['value_id'])
                  for field in story.get('custom_fields', [])
              ],
              created=story['created_at'],
              updated=story['updated_at'],
              description=story.get('description'),
              labels=[labels[label['id']]
                      for label in story.get('labels', [])],
              active=True
              )

        for story in stories
    ]

    deactivate_q = update(Story).values(active=False)
    db.execute(deactivate_q)
    await update_saved(db, Story, db_stories)

    return {'message': f'{len(db_stories)} stories imported',
            'total': len(db_stories)}
