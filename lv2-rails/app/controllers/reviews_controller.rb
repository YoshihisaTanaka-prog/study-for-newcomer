class ReviewsController < ApplicationController
  def create
    @restaurant = Restaurant.find(params[:restaurant_id])
    @review = @restaurant.reviews.build(review_params)

    respond_to do |format|
      if @review.save
        format.html { redirect_to @restaurant, notice: "匿名コメントを投稿しました。" }
        format.json { render :show, status: :created, location: restaurant_path(@restaurant) }
      else
        @restaurant = Restaurant.includes(:office, :payment_methods, :reviews).find(params[:restaurant_id])
        format.html { render "restaurants/show", status: :unprocessable_entity }
        format.json do
          render json: { errors: @review.errors.full_messages }, status: :unprocessable_entity
        end
      end
    end
  end

  private

  def review_params
    params.require(:review).permit(:body, :rating, :visited_on)
  end
end
