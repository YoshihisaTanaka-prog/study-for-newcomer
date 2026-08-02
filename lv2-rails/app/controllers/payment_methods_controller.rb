class PaymentMethodsController < ApplicationController
  def index
    @payment_methods = PaymentMethod.order(:name)

    respond_to do |format|
      format.json
      format.html { redirect_to restaurants_path }
    end
  end
end
