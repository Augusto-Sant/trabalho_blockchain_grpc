from fastapi import APIRouter, HTTPException, Depends
from models.dtos import InsuranceIn, InsuranceOut, UserRead, UserCreate
from models.user import User
import grpc
from grpc_utils import insurance_service_pb2, insurance_service_pb2_grpc
from db import get_db
import asyncio
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter()


@router.post("/users", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/users", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


# -------------- Insurance GRPC -------------------
@router.get("/health_grpc_server")
async def grpc_health_check():
    try:
        # Use an async executor to avoid blocking event loop
        loop = asyncio.get_event_loop()

        def grpc_call():
            with grpc.insecure_channel("localhost:50051") as channel:
                stub = insurance_service_pb2_grpc.InsuranceServiceStub(channel)
                # call a lightweight method
                return stub.GetAllInsurances(insurance_service_pb2.Empty())

        # Run grpc call in threadpool to not block async loop
        response = await loop.run_in_executor(None, grpc_call)

        # If call succeeds, return healthy + number of insurances
        count = len(response.insurances)
        return {"status": "healthy", "insurance_count": count}
    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=f"gRPC server unreachable: {e}")


@router.post("/insurance", response_model=dict)
async def register_insurance(data: InsuranceIn):
    def grpc_call():
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = insurance_service_pb2_grpc.InsuranceServiceStub(channel)
            request = insurance_service_pb2.InsuranceRequest(id=data.id, value=data.value)
            return stub.RegisterInsurance(request)

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, grpc_call)
        return {"success": response.success, "id": response.id}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e}")


@router.get("/insurance", response_model=List[InsuranceOut])
async def list_insurances():
    def grpc_call():
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = insurance_service_pb2_grpc.InsuranceServiceStub(channel)
            return stub.GetAllInsurances(insurance_service_pb2.Empty())

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, grpc_call)
        return [InsuranceOut(id=i.id, value=i.value, created_at=i.created_at) for i in response.insurances]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e}")
