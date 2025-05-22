from fastapi import FastAPI, HTTPException
import pandas as pd
app = FastAPI()
users_df = pd.read_csv("users.csv")
restaurants_df = pd.read_csv("restaurants.csv")
restaurants_df["normalized_rating"] = (
    (restaurants_df["avg_rating"] - restaurants_df["avg_rating"].min()) /
    (restaurants_df["avg_rating"].max() - restaurants_df["avg_rating"].min())
)
def recommend_restaurants(user_id):
    user = users_df[users_df["user_id"] == user_id]
    if user.empty:
        return None
    user = user.iloc[0]
    
    recommendations = []
    for _, restaurant in restaurants_df.iterrows():
        score = 0
        if restaurant["cuisine"].lower() == user["preferred_cuisine"].lower():
            score += 0.5
        if restaurant["location"].lower() == user["location"].lower():
            score += 0.3
        score += 0.2 * restaurant["normalized_rating"]
        recommendations.append({
            "restaurant_id": restaurant["restaurant_id"],
            "name": restaurant["name"],
            "score": round(score, 3)
        })

    top_recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)[:3]
    return top_recommendations

@app.get("/recommend/{user_id}")
def get_recommendations(user_id: str):
    result = recommend_restaurants(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "recommendations": result}
