class OfficesController < ApplicationController
  def index
    @offices = Office.order(:name)

    respond_to do |format|
      format.json
      format.html { redirect_to restaurants_path }
    end
  end
end
