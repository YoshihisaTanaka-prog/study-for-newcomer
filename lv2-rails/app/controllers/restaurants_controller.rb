class RestaurantsController < ApplicationController
  before_action :set_restaurant, only: [:show, :edit, :update]
  before_action :set_form_options, only: [:index, :new, :create, :edit, :update]

  def index
    @restaurants = Restaurant.includes(:office, :payment_methods).newest_first
    @restaurants = @restaurants.where(office_id: params[:office_id]) if params[:office_id].present?
    @restaurants = @restaurants.where("genre ILIKE ?", "%#{params[:genre]}%") if params[:genre].present?
    @restaurants = @restaurants.where("price_min <= ?", params[:budget]) if params[:budget].present?

    if params[:payment_method_ids].present?
      @restaurants = @restaurants
        .joins(:payment_methods)
        .where(payment_methods: { id: params[:payment_method_ids] })
        .distinct
    end

    respond_to do |format|
      format.html
      format.json
    end
  end

  def show
    @review = Review.new

    respond_to do |format|
      format.html
      format.json
    end
  end

  def new
    @restaurant = Restaurant.new
  end

  def edit
  end

  def create
    @restaurant = Restaurant.new(restaurant_params)

    respond_to do |format|
      if @restaurant.save
        format.html { redirect_to @restaurant, notice: "飲食店を匿名で投稿しました。" }
        format.json { render :show, status: :created, location: @restaurant }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json do
          render json: { errors: @restaurant.errors.full_messages }, status: :unprocessable_entity
        end
      end
    end
  end

  def update
    respond_to do |format|
      if @restaurant.update(restaurant_params)
        format.html { redirect_to @restaurant, notice: "飲食店の投稿を更新しました。" }
        format.json { render :show, status: :ok, location: @restaurant }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json do
          render json: { errors: @restaurant.errors.full_messages }, status: :unprocessable_entity
        end
      end
    end
  end

  private

  def set_restaurant
    @restaurant = Restaurant.includes(:office, :payment_methods, :reviews).find(params[:id])
  end

  def set_form_options
    @offices = Office.order(:name)
    @payment_methods = PaymentMethod.order(:name)
  end

  def restaurant_params
    params.require(:restaurant).permit(
      :office_id,
      :name,
      :genre,
      :tabelog_url,
      :price_min,
      :price_max,
      :memo,
      payment_method_ids: []
    )
  end
end
