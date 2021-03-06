import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from time import time
import linecache

import numpy as np
from numpy import load
from scipy.sparse import csr_matrix, csc_matrix
from scipy.spatial.distance import cosine

from Core.LatentFactor import estimate_user_rating
from Core.RandomHyperplanes import locality_sensitive_hashing, locality_sensitive_hashing_movie, calculate_user_similarity
from Oracles import Sebastian
from Factories.CreateSignatureMatrices import generate_user_signature


def get_movie_title(id):
	return linecache.getline("../Files/MovieList.txt", id)


def test_sebastian_recommendation(user_id, desired_movie_count=10):
	# Get recommendations.
	recommendation_list = Sebastian.recommend_movie(user_id, desired_movie_count)
	# Print movie titles.
	for movie_id, rating in recommendation_list:
		print get_movie_title(movie_id), rating


def test_latent_factor(user_id, movie_id):
	ranking = estimate_user_rating(user_id, movie_id)
	loader = load("../Files/TrainingMatrixCSR.npz")
	utility_csr = csr_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=loader["shape"])
	real = utility_csr[user_id, movie_id]
	print "User %d Movie %d. Real ranking: %f. Estimated ranking: %f" % (user_id, movie_id, real, ranking)


def test_lsh_speed(num_bands):
	start_time = time()
	signature = np.load("../Files/UserSignature.npy")
	pairs = locality_sensitive_hashing(signature, num_bands)
	print "Finished in %d seconds." % (time() - start_time)


def test_lsh(num_bands):
	start_time = time()
	signature = np.load("../Files/UserSignature.npy")
	pairs = locality_sensitive_hashing(signature, num_bands)
	print "LSH completed in %d seconds." % (time() - start_time)

	size = len(pairs)
	count = 0
	distances = []
	similarities = []
	for pair in pairs:
		num = len(pair)
		for i in xrange(0, num):
			for j in xrange(i+1, num):
				_, distance,similarity = calculate_user_similarity(pair[i], pair[j], signature)
				#distances.append(distance)
				similarities.append(similarity)
		
		count += 1
		if count % 1000 == 0:
			print "%d/%d completed." % (count, size)

	print "---"
	#print "Distances: %d" % len(distances)
	print "Similarities: %d" % len(similarities)
	count1 = 0
	count2 = 0
	count3 = 0
	count4 = 0
	count5 = 0
	for i in similarities:
		if i > 0.3:
			count1 += 1
		if i > 0.5:
			count2 += 1
		if i > 0.7:
			count3 += 1
		if i > 0.9:
			count4 += 1
		if i == 1.0:
			count5 += 1
	print "LSH with %d bands." % num_bands
	print "Similarity greater than 0.3: %d" % count1
	print "Similarity greater than 0.5: %d" % count2
	print "Similarity greater than 0.7: %d" % count3
	print "Similarity greater than 0.9: %d" % count4
	print "Similarity equal to 1.0:     %d" % count5
	#print "Distances less than 0.35: %d" % count1
	#print "Distances less than 0.50: %d" % count2
	#print "Distances less than 0.75: %d" % count3
	#print "Distances less than 1.00: %d" % count4
	print "Finished in %d seconds." % (time() - start_time)


def test_lsh_movie(num_bands):
	signature = np.load("../Files/MovieSignature.npy")
	pairs = locality_sensitive_hashing_movie(signature[0:2000], num_bands)
	print "---"

	loader = load("../Files/NormalizedUtilityMatrixCSC.npz")
	n_utility_csc = csc_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=loader["shape"])

	distances = []
	for pair in pairs:
		num = len(pair)
		for i in xrange(0, num):
			u = n_utility_csc.getcol(pair[i]).toarray()
			for j in xrange(i + 1, num):
				v = n_utility_csc.getcol(pair[j]).toarray()
				distances.add(cosine(u, v))

	print "---"
	print "Distances: %d" % len(distances)
	count = 0
	for i in distances:
		if i <= 0.5:
			count += 1
	print "Distances less than 0.50: %d" % count
	print sorted(distances)


def test_random_hyperplanes_similarity(i=62500, regenerate=False, vector_count=120):
	start_time = time()

	if regenerate:
		generate_user_signature(vector_count)

	# Load necessary matrices.
	loader = load("../Files/TrainingMatrixCSR.npz")
	utility_csr = csr_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=loader["shape"])
	signature = np.load("../Files/UserSignature.npy")

	for j in [1, 2, 62500]:
		u = utility_csr.getrow(i).toarray()
		v = utility_csr.getrow(j).toarray()
		angle, distance = calculate_user_similarity(i, j, signature)

		print "User %d and Candidate %d" % (i, j)
		print "Angle and Distance: %d degrees, %f" % (angle, distance)
		print "Original Distance:  %f\n" % cosine(u, v)

	print "\n%f seconds elapsed." % (time() - start_time)


def test_all(user_id, movie_id):
	start_time = time()
	print "Latent Factor"
	test_latent_factor(user_id, movie_id)
	print "Finished in %d seconds.\n" % (time() - start_time)


# Test cases.
#test_random_hyperplanes_similarity(regenerate=True)
#test_lsh(5)
#test_lsh_speed(4)
#generate_movie_signature()
#test_lsh_movie(8)
#test_all(3, 590)
# print recommend_movie(10)
# print MovieList.movie_list[10]
# print MovieList.movie_list
