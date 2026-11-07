"""Fail-closed Fernet key rotation for encrypted provider tokens (maintenance only)."""
import argparse
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from cryptography.fernet import Fernet,InvalidToken
from sqlalchemy import select,update
from sqlalchemy.orm import Session
from app.db import ChannelConnection,engine_for
from app.integrations.adapters import cryptor


def rotation_report(session,*,apply=False):
    key=os.getenv('INTEGRATION_ENCRYPTION_KEY','').strip()
    if not key:raise RuntimeError('Нет текущего ключа интеграций')
    try:
        primary=Fernet(key.encode('ascii'))
        multi=cryptor()
    except Exception as exc:raise RuntimeError('Неверные ключи шифрования') from exc
    rows=session.execute(select(ChannelConnection.id,ChannelConnection.encrypted_credentials)
        .where(ChannelConnection.encrypted_credentials.is_not(None))
        .order_by(ChannelConnection.id)).all()
    old=[];current=0
    for channel_id,encrypted in rows:
        try:primary.decrypt(encrypted.encode('ascii'));current+=1
        except InvalidToken:
            try:multi.decrypt(encrypted.encode('ascii'))
            except Exception as exc:raise RuntimeError('Часть токенов не расшифровывается; ничего не изменено') from exc
            old.append((channel_id,encrypted))
    if apply:
        for channel_id,encrypted in old:
            fresh=multi.rotate(encrypted.encode('ascii')).decode('ascii')
            primary.decrypt(fresh.encode('ascii'))
            result=session.execute(update(ChannelConnection).where(
                ChannelConnection.id==channel_id,ChannelConnection.encrypted_credentials==encrypted)
                .values(encrypted_credentials=fresh))
            if result.rowcount!=1:
                session.rollback();raise RuntimeError('Токен изменился параллельно, изменения отменены')
        session.commit()
    return {'checked':len(rows),'already_current':current,'old_key_records':len(old),
            'rotated':len(old) if apply else 0}


def main():
    parser=argparse.ArgumentParser(description='Безопасная смена ключей интеграций')
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true')
    group.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env',override=False)
    engine=engine_for()
    try:
        with Session(engine) as session:
            result=rotation_report(session,apply=args.apply)
            for key,value in result.items():print(key,':',value)
        return 0
    except Exception:
        print('Не удалось завершить операцию; секреты не печатаются.',file=sys.stderr)
        return 2
    finally:engine.dispose()
if __name__=='__main__':raise SystemExit(main())
