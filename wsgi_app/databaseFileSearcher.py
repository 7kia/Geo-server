class DatabaseFileSearcher:
    @classmethod
    def search_best_db_file(cls, point, db_file):
        # global DB_DIR
        # db_files = os.listdir(DB_DIR)
        # min_size = MIN_SIZE_DEFAULT
        # best_file = 'undefined'
        # for curr_file in filter( lambda fname: fname.find(db_file) == 0, db_files):
        # 	if isInside(curr_file,point):
        # 		size = getAreaSize(curr_file)
        # 		if size <= min_size:
        # 			min_size = size
        # 			best_file = curr_file
        # return best_file
        best_file = db_file + ".sqlite"
        return best_file

    @classmethod
    def search_best_db_file_by_two_points(cls, point1, point2, db_file):
        # global DB_DIR
        # db_files = os.listdir(DB_DIR)
        # min_size = MIN_SIZE_DEFAULT
        # best_file = 'undefined'
        # for curr_file in filter(lambda fname: fname.find(db_file) == 0, db_files):
        #     if isInside(curr_file, point1, point2):
        #         size = getAreaSize(curr_file)
        #         if size <= min_size:
        #             min_size = size
        #             best_file = curr_file
        best_file = db_file + ".sqlite"
        return best_file
