Rails.application.routes.draw do
  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  root "restaurants#index"

  resources :offices, only: [:index]
  resources :payment_methods, only: [:index]
  resources :restaurants, only: [:index, :show, :new, :create, :edit, :update] do
    resources :reviews, only: [:create]
  end
end
